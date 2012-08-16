import re

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
    