from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from django_markdown.widgets import MarkdownWidget as RichText

class HiddenViewInput (forms.HiddenInput):
  def render (self, name, value, attrs=None):
    ret = super(HiddenViewInput, self).render(name, value, attrs=attrs)
    if value:
      ret = '<strong style="display: block; padding-top: 4px;">' + str(value) + '</strong>' + ret
      
    return mark_safe(ret)
    
class RichTextOld (forms.Textarea):
  def render (self, name, value, attrs=None):
    ret = super(RichText, self).render(name, value, attrs=attrs)
    ret = ret.replace('<textarea ', '<textarea class="pizza_editor" ')
    
    return mark_safe(ret)
    
  class Media:
    css = {'all': ('ks/css/pizza_editor.css',)}
    
    js = (
      'ks/ckeditor/ckeditor.js',
      'ks/js/pizza_editor.js',
    )
    