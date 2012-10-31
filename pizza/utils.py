import datetime
import hashlib

from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import utc

PIZZA_CACHE_TIMEOUT = getattr(settings, 'PIZZA_CACHE_TIMEOUT', 600)

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
  