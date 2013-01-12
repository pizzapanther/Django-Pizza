from django import template
from django.db import models

register = template.Library()

from ..models import Blurb

@register.filter
def get_blurb (bkey):
  try:
    b = Blurb.objects.get(slug=bkey)
    
  except models.ObjectDoesNotExist:
    return None
    
  else:
    if b.content:
      return b.content
      
    return None
    