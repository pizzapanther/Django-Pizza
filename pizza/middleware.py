import re
import urlparse
import urllib

from django import http
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache

PIZZA_SITES_KEY = getattr(settings, 'PIZZA_SITES_KEY', 'PIZZA_SITES')
PIZZA_DEFAULT_SITE_KEY = getattr(settings, 'PIZZA_DEFAULT_SITE_KEY', 'PIZZA_DEFAULT_SITE')

class Siteware (object):
  def process_request (self, request):
    request.pizza_site = self.default_site()
    
    for s in self.get_sites():
      if re.search(s['domain'], request.get_host(), re.I):
        request.pizza_site = s
        
    return None
    
  def get_sites (self):
    ret = cache.get(PIZZA_SITES_KEY)
    if ret is None:
      ret = Site.objects.all().values()
      cache.set(PIZZA_SITES_KEY, ret)
      
    return ret
    
  def default_site (self):
    ret = cache.get(PIZZA_DEFAULT_SITE_KEY)
    if ret is None:
      ret = Site.objects.filter(id=settings.SITE_ID).values()[0]
      cache.set(PIZZA_DEFAULT_SITE_KEY, ret)
      
    return ret
    
class RememberAdminQuery:
  def process_request (self, request):
    if request.method == 'GET' and request.path.startswith('/admin'):
      if request.REQUEST.get('nocache', '') == '1':
        return None
        
      other = re.search("^/admin/(\S+?)/(\S+?)/\S+$", request.path)
      found = re.search("^/admin/(\S+?)/(\S+?)/$", request.path)
      clear = request.REQUEST.get('__clearqs', '')
      pop = request.REQUEST.get('_popup', '0')
      
      if not other and found:
        key = 'aquery-%s-%s-%s' % (pop, found.group(1), found.group(2))
        
        if clear == '1':
          try:
            del request.session[key]
            
          except:
            pass
            
          if pop == '1':
            url = request.path + '?_popup=1'
            t = request.REQUEST.get('t', '')
            if t:
              url += '&t=' + urllib.quote(t)
              
            return http.HttpResponseRedirect(url)
            
          return http.HttpResponseRedirect(request.path)
          
        qsdict = urlparse.parse_qs(request.META['QUERY_STRING'])
        for k in ('t', 'pop'):
          try:
            del qsdict[k]
            
          except:
            pass
            
        if len(qsdict.keys()) > 0:
          request.session[key] = request.META['QUERY_STRING']
          
        else:
          try:
            qs = request.session[key]
            
          except:
            pass
            
          else:
            if qs != request.META['QUERY_STRING']:
              return http.HttpResponseRedirect('%s?%s' % (request.path, qs))
              
    return None
    