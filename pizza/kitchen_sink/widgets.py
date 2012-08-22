from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

class RichText (forms.Textarea):
  def render (self, name, value, attrs=None):
    ret = super(RichText, self).render(name, value, attrs=attrs)
    ret += """
    <script type="text/javascript">
      CKEDITOR.replace( \'id_%s\', {customConfig : \'%sks/js/ckconfig.js\'});
    </script>
    """ % (
      name,
      settings.STATIC_URL
    )
    
    return mark_safe(ret)
    
  class Media:
    #css = {'all': ('ks/redactor/redactor.css', 'ks/redactor/admin.css')}
    js = (
      'ks/ckeditor/ckeditor.js',
    )
    