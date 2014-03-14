from django import template
from django.db import models

register = template.Library()

from ..models import Blurb

@register.filter
def get_blurb (bkey):
  ret = None
  
  try:
    b = Blurb.objects.get(slug=bkey)
    
  except models.ObjectDoesNotExist:
    ret = None
    
  else:
    if b.content:
      ret = b.content
      
  if ret is None:
    ret = 'No content found for {}'.format(bkey)
    
  return ret
  