import datetime
import hashlib

from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import utc
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

PIZZA_CACHE_TIMEOUT = getattr(settings, 'PIZZA_CACHE_TIMEOUT', 600)

USING_GRAPPELLI = 'grappelli' in settings.INSTALLED_APPS

def now ():
  return datetime.datetime.utcnow().replace(tzinfo=utc)
  
def post_render (response, key, timeout):
  cache.set(key, response, timeout)
  
def generate_cache_key (request):
  unhashed = None
  
  if request.method != 'POST':
    unhashed = request.method + request.build_absolute_uri()
    if hasattr(request, 'pizza_site') and request.pizza_site:
      unhashed += str(request.pizza_site['id'])
      
  return unhashed
  
def pizza_cache (timeout=PIZZA_CACHE_TIMEOUT, key_generator=generate_cache_key):
  def decorator (target):
    def wrapper (*args, **kwargs):
      request = args[0]
      key = key_generator(request)
      if key:
        key = hashlib.sha1(key).hexdigest()
        
      preview = request.REQUEST.get('preview', '')
      version = request.REQUEST.get('version', '')
      
      if key is None:
        response = target(*args, **kwargs)
        
      elif (preview == '1' or version != '') and request.user.is_authenticated() and request.user.is_staff:
        response = target(*args, **kwargs)
        if preview == '1':
          cache.delete(key)
          
      else:
        response = cache.get(key, None)
        if response:
          pass
          
        else:
          response = target(*args, **kwargs)
          if hasattr(response, 'add_post_render_callback'):
            response.add_post_render_callback(lambda r: post_render(r, key, timeout))
            
          else:
            cache.set(key, response, timeout)
            
      return response
      
    return wrapper
    
  if type(timeout) == type(decorator):
    t = timeout
    timeout = PIZZA_CACHE_TIMEOUT
    return decorator(t)
    
  return decorator
  
def cached_method (target):
  def wrapper(*args, **kwargs):
    obj = args[0]
    name = '_' + target.__name__
    
    if not hasattr(obj, name):
      value = target(*args, **kwargs)
      setattr(obj, name, value)
      
    return getattr(obj, name)
    
  return wrapper
  
def update_attrs (obj, clone, exclude=[]):
  for f in obj._meta.fields:
    if f.name not in exclude:
      if not isinstance(f, models.AutoField) and not isinstance(f, models.OneToOneField) and not f in obj._meta.parents.values():
        setattr(clone, f.name, getattr(obj, f.name))
        
  clone.save()
  
def copy_inlines (obj, newobj):
  #TODO: Make this more generic so it works on generic relations and normal inlines
  pass
  
def copy_model_instance (obj):
  initial = {}
  for f in obj._meta.fields:
    if not isinstance(f, models.AutoField) and not isinstance(f, models.OneToOneField) and not f in obj._meta.parents.values():
      initial[f.name] = getattr(obj, f.name)
      
  return obj.__class__(**initial)
  
def copy_many_to_many (obj, newobj):
  for f in obj._meta.many_to_many:
    org_m2m = getattr(obj, f.name)
    new_m2m = getattr(newobj, f.name)
    
    if isinstance(f, models.ManyToManyField):
      new_m2m.clear()
      
      for thingy in org_m2m.all():
        new_m2m.add(thingy)
        
    elif isinstance(f, generic.GenericRelation):
      new_m2m.clear()
      
      for thingy in org_m2m.all():
        new_thingy = copy_model_instance(thingy)
        new_thingy.content_object = newobj
        new_thingy.save()
        