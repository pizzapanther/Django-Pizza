from django import template
from django.conf import settings
from django.db import models

from django_markdown.utils import markdown

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
      ret = markdown(b.content, extensions=settings.MARKDOWN_EXTENSIONS)
      
  if ret is None:
    ret = 'No content found for {}'.format(bkey)
    
  return ret
  