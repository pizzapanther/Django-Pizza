import datetime
import cPickle as pickle

from django import forms
from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.defaultfilters import date
from django.contrib.admin.widgets import AdminSplitDateTime, ForeignKeyRawIdWidget
from django.contrib import admin
from django.db.models.fields.related import ManyToOneRel
from django.utils.timezone import utc
from django.db.models.signals import post_save
from django.core.cache import cache
from django.dispatch import receiver

from .widgets import RichText
from pizza.middleware import PIZZA_SITES_KEY, PIZZA_DEFAULT_SITE_KEY

from sorl.thumbnail import get_thumbnail

PIZZA_FILE_DIR = getattr(settings, 'PIZZA_FILE_DIR', 'pizza/files/%Y-%m')
PIZZA_IMAGE_DIR = getattr(settings, 'PIZZA_IMAGE_DIR', 'pizza/images/%Y-%m')

@receiver(post_save, sender=Site)
def site_cache (sender, **kwargs):
  cache.delete(PIZZA_SITES_KEY)
  cache.delete(PIZZA_DEFAULT_SITE_KEY)
  
class SitesMixin (object):
  def _sites (self):
    ret = ''
    for s in self.sites.all():
      ret += s.name + ', '
      
    if ret:
      ret = ret[:-2]
      
    return ret
    
class ViewFileMixin (object):
  def view (self):
    return '<a href="%s" target="_blank">View File</a>' % self.file.url
    
  view.allow_tags = True
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains")
    
class File (ViewFileMixin, models.Model):
  title = models.CharField(max_length=255)
  file = models.FileField(upload_to=PIZZA_FILE_DIR)
  added_by = models.ForeignKey('auth.User')
  modified = models.DateTimeField(auto_now=True, auto_now_add=True)
  
  def __unicode__ (self):
    return self.title
    
  class Meta:
    ordering = ("title",)
    
class Image (ViewFileMixin, models.Model):
  title = models.CharField(max_length=255)
  file = models.ImageField(upload_to=PIZZA_IMAGE_DIR)
  added_by = models.ForeignKey('auth.User')
  modified = models.DateTimeField(auto_now=True, auto_now_add=True)
  
  def __unicode__ (self):
    return self.title
    
  class Meta:
    ordering = ("title",)
    
  def Thumbnail (self):
    im = get_thumbnail(self.file, '64x64')
    return '<img src="%s" alt="">' % im.url
    
  Thumbnail.allow_tags = True
  
class Template (models.Model):
  name = models.CharField(max_length=255)
  template = models.CharField(max_length=255, choices=settings.PIZZA_TEMPLATES)
  
  def __unicode__ (self):
    return self.name
    
  class Meta:
    ordering = ("name",)
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "name__icontains",)
    
EDITORTYPES = (
  ('rich', 'Rich Text'),
  ('plain', 'Plain Text'),
  ('richone', 'Rich One Line Text'),
  ('plainone', 'Plain One Line Text'),
  ('image', 'Image')
)

class TemplateRegion (models.Model):
  template = models.ForeignKey(Template)
  name = models.CharField('Name', max_length=255)
  cvar = models.SlugField('Variable Name', max_length=255)
  etype = models.CharField("Editor Type", choices=EDITORTYPES, max_length=25)
  
  order = models.IntegerField('Order')
  
  def __unicode__ (self):
    return self.name
    
  class Meta:
    ordering = ("order",)
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "name__icontains",)
    
  def form_field (self, initial=None):
    if self.etype == 'image':
      return forms.ModelChoiceField(
        queryset=Image.objects.all(),
        required=False, label=self.name,
        widget=ForeignKeyRawIdWidget(ManyToOneRel(Image, 'id'), admin.site),
        initial=initial
      )
      
    elif self.etype == 'rich':
      return forms.CharField(max_length=255, required=False, label=self.name, widget=RichText, initial=initial)
      
    elif self.etype == 'plain':
      return forms.CharField(required=False, label=self.name, widget=forms.Textarea, initial=initial)
      
    return forms.CharField(max_length=255, required=False, label=self.name, initial=initial, widget=forms.TextInput(attrs={'class': 'vTextField'}))
    
class Page (SitesMixin, models.Model):
  url = models.CharField('URL', max_length=255, help_text='Examples: / = HomePage, /some_page, /some_page/sub_page')
  template = models.ForeignKey(Template)
  
  sites = models.ManyToManyField(Site)
  
  class Meta:
    ordering = ('url',)
    
  def __unicode__ (self):
    return self.url
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "url__icontains",)
    
  def Settings (self):
    return '<a href="./%d/?settings=1">Edit Settings</a>' % self.id
    
  Settings.allow_tags = True
  
  def published_version (self, version=None):
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    if version:
      qs = self.version_set.filter(id=version)
      
    else:
      qs = self.version_set.filter(publish__lte=now)
      
    if qs.count() > 0:
      return qs[0]
      
    return None
    
  def version_iter (self):
    ret = []
    for v in self.unpublished_versions():
      ret.append(v)
      
    for v in self.published_versions():
      ret.append(v)
      
    return ret
    
  def published_versions (self):
    return self.version_set.filter(publish__isnull=False)
    
  def unpublished_versions (self):
    return self.version_set.filter(publish__isnull=True)
    
  def admin_form (self, version):
    class Meta:
      model = Version
      exclude = ('page', 'content')
      
    fields = {
      'title': forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'vTextField'})),
      'keywords': forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'vTextField'})),
      'desc': forms.CharField(max_length=255, label='Description', required=False, widget=forms.TextInput(attrs={'class': 'vTextField'})),
      'publish': forms.DateTimeField(required=False, widget=AdminSplitDateTime),
      
      'Meta': Meta
    }
    
    content = version.get_content()
    for tr in self.template.templateregion_set.all():
      initial = None
      if content.has_key(tr.cvar):
        initial = content[tr.cvar]
        
      fields['generatedfield_' + tr.cvar] = tr.form_field(initial=initial)
      
    return type('AdminForm', (forms.ModelForm,), fields)
    
  def Versions (self):
    return '<div id="view_versions_%d"><a href="javascript: void(0);" onclick="get_versions(%d)">View Versions</a></div>' % (self.id, self.id)
    
  Versions.allow_tags = True
  
  def View_Published (self):
    return '<a href="%s" target="_blank">View</a>' % self.url
    
  View_Published.allow_tags = True
    
class Redirect (SitesMixin, models.Model):
  url = models.CharField('URL', max_length=255, help_text='Examples: /, /some_page, /some_page/sub_page')
  goto = models.CharField('Redirect To', max_length=255, help_text='Relative urls should begin with a slash (/), absolute urls should begin with "http://"')
  
  sites = models.ManyToManyField(Site)
  
  class Meta:
    ordering = ('url',)
    
  def __unicode__ (self):
    return self.url
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "url__icontains",)
    
class Version (models.Model):
  page = models.ForeignKey(Page)
  title = models.CharField(max_length=255)
  
  keywords = models.CharField(max_length=255, blank=True, null=True)
  desc = models.CharField('Description', max_length=255, blank=True, null=True)
  
  publish = models.DateTimeField(blank=True, null=True)
  
  content = models.TextField()
  
  def get_context (self):
    c = self.get_content()
    for tr in self.page.template.templateregion_set.all():
      if tr.etype == 'image' and c.has_key(tr.cvar) and c[tr.cvar]:
        try:
          c[tr.cvar] = Image.objects.get(id=c[tr.cvar])
          
        except models.ObjectDoesNotExist:
          pass
        
    return c
    
  def get_content (self):
    if self.content:
      return pickle.loads(str(self.content))
      
    return {}
    
  def set_content (self, d):
    self.content = pickle.dumps(d)
    
  class Meta:
    ordering = ('-publish', 'id')
    
  def __unicode__ (self):
    return self.page.url
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains",)
    