from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class RichText (forms.Textarea):
  def render (self, name, value, attrs=None):
    ret = super(RichText, self).render(name, value, attrs=attrs)
    ret += """
    <script type="text/javascript">
        $(document).ready(function() {
          $('#id_%s').redactor();
        });
    </script>
    """ % name
    
    return mark_safe(ret)
    
  class Media:
    css = {'all': ('ks/redactor/redactor.css', 'ks/redactor/admin.css')}
    js = (
      'ks/js/jquery-1.8.0.min.js',
      'ks/redactor/redactor.min.js',
    )
    