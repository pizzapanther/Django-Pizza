import json

from django import http
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.urlresolvers import resolve

from sorl.thumbnail import get_thumbnail

from .models import Page, Redirect, Image
from pizza.utils import pizza_cache

@pizza_cache
def page (request):
  version = request.GET.get('version', '')
  
  qs = Redirect.objects.filter(url=request.path, sites__id=request.pizza_site['id'])
  if qs.count() > 0:
    return http.HttpResponseRedirect(qs[0].goto)
    
  qs = Page.objects.filter(url=request.path, sites__id=request.pizza_site['id'])
  if qs.count() > 0:
    if version and request.user.is_authenticated():
      pubver = qs[0].published_version(version)
      
    else:
      pubver = qs[0].published_version()
      
    if pubver:
      context = pubver.get_context()
      
      c = {
        'page': qs[0],
        'title': pubver.title,
        'keywords': pubver.keywords,
        'description': pubver.desc
      }
      
      c.update(context)
      return TemplateResponse(request, qs[0].tpl, c)
      
  qs = Page.objects.filter(url__iexact=request.path, sites__id=request.pizza_site['id'])
  if qs.count() > 0:
    if qs[0].published_version():
      return http.HttpResponseRedirect(qs[0].url)
      
  if not request.path.endswith('/'):
    match = resolve(request.path + '/')
    if match.url_name != 'pizza.utils.wrapper':
      url = request.path + '/'
      if request.META['QUERY_STRING']:
        url += '?' + request.META['QUERY_STRING']
        
      return http.HttpResponseRedirect(url)
      
  raise http.Http404
  
@staff_member_required
def admin_image_list (request):
  images = []
  
  for obj in Image.objects.all().order_by("-modified")[:100]:
    im = get_thumbnail(obj.file, '75x75', crop='center')
    images.append({"thumb": im.url, "image": obj.file.url})
    
  return http.HttpResponse(json.dumps(images), mimetype="application/json")
  
@csrf_exempt
@require_POST
@staff_member_required
def admin_image_upload (request):
  images = []
  for f in request.FILES.getlist("file"):
    obj = Image.objects.create(file=f, title=f.name, added_by=request.user)
    images.append({"filelink": obj.file.url})
    
  return http.HttpResponse(json.dumps(images), mimetype="application/json")
  
@staff_member_required
def admin_editon (request):
  goto = request.GET.get('goto', '')
  response = http.HttpResponseRedirect(goto)
  
  response.set_cookie('PIZZA_EDIT', value='ON', max_age=60 * 60 * 24, httponly=False)
  return response
  