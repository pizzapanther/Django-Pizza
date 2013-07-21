import datetime
import cPickle as pickle
import urllib

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
from django.core.urlresolvers import reverse

from .widgets import RichText
from pizza.middleware import PIZZA_SITES_KEY, PIZZA_DEFAULT_SITE_KEY
from pizza.utils import cached_method

from sorl.thumbnail import get_thumbnail

PIZZA_FILE_DIR = getattr(settings, 'PIZZA_FILE_DIR', 'pizza/files/%Y-%m')
PIZZA_IMAGE_DIR = getattr(settings, 'PIZZA_IMAGE_DIR', 'pizza/images/%Y-%m')
PIZZA_TEMPLATES = getattr(settings, 'PIZZA_TEMPLATES', ())

EDITORTYPES = (
  ('rich', 'Rich Text'),
  ('plain', 'Plain Text'),
  ('richone', 'Rich One Line Text'),
  ('plainone', 'Plain One Line Text'),
  ('image', 'Image')
)

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
    
class SlideshowMixin (object):
  @cached_method
  def first_image (self):
    if self.imageset:
      if self.imageset.imagesetitem_set.all().count() > 0:
        return self.imageset.imagesetitem_set.all()[0].image
        
    if self.image:
      return self.image
      
    return None
    
  @cached_method
  def image_list (self):
    ret = []
    if self.imageset:
      return self.imageset.imagesetitem_set.all()
      
    elif self.image:
      ret.append(self.image)
      
    return ret
    
class ViewFileMixin (object):
  def view (self):
    return '<a href="%s" target="_blank">View File</a>' % self.file.url
    
  view.allow_tags = True
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains")
    
class Blurb (models.Model):
  title = models.CharField(max_length=255)
  slug = models.SlugField('Key', unique=True)
  etype = models.CharField("Editor Type", choices=EDITORTYPES, max_length=25)
  content = models.TextField(blank=True, null=True)
  
  def __unicode__ (self):
    return self.title
    
  class Meta:
    ordering = ('title',)
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains", "slug__icontains")
    
  def Settings (self):
    return '<a href="./%d/?settings=1">Edit Settings</a>' % self.id
    
  Settings.allow_tags = True
  
class File (ViewFileMixin, models.Model):
  title = models.CharField(max_length=255)
  file = models.FileField(upload_to=PIZZA_FILE_DIR)
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains", "file__icontains")
    
  def __unicode__ (self):
    return self.title
    
  class Meta:
    ordering = ("title",)
    
class Image (ViewFileMixin, models.Model):
  title = models.CharField(max_length=255)
  file = models.ImageField(upload_to=PIZZA_IMAGE_DIR)
  
  caption = models.CharField(max_length=255, blank=True, null=True)
  caption_url = models.CharField('Caption URL', max_length=255, blank=True, null=True)
  
  credit = models.CharField('Photo Credit', max_length=255, blank=True, null=True)
  credit_url = models.CharField('Photo Credit URL', max_length=255, blank=True, null=True)
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains", "file__icontains")
    
  def __unicode__ (self):
    return self.title
    
  class Meta:
    ordering = ("title",)
    
  def Thumbnail (self):
    im = get_thumbnail(self.file, '64x64')
    return '<img src="%s" alt="">' % im.url
    
  Thumbnail.allow_tags = True
  
  def cap (self):
    return self.caption
    
  def cap_url (self):
    return self.caption_url
    
  def cred (self):
    return self.credit
    
  def cred_url (self):
    return self.credit_url
    
CAPTYPES = (
  ('override', 'Use image captions and credits, and override if filled in below.'),
  ('mine', 'Use captions and credits from below only'),
)

class ImageSet (models.Model):
  title = models.CharField(max_length=255)
  captype = models.CharField('Caption/Credit Override', max_length=10, choices=CAPTYPES, default='override')
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains")
    
  def __unicode__ (self):
    return self.title
    
  class Meta:
    ordering = ("title",)
    verbose_name = 'Image Set'
    
  def Thumbnails (self):
    ret = ''
    for item in self.imagesetitem_set.all():
      ret += item.image.Thumbnail().replace('<img ', '<img style="float: left; margin: 0 10px 10px 0;" ')
      
    ret += '<div style="clear: both;"></div>'
    return ret
    
  Thumbnails.allow_tags = True
  
class ImageSetItem (models.Model):
  image = models.ForeignKey(Image)
  imageset = models.ForeignKey(ImageSet)
  
  caption = models.CharField(max_length=255, blank=True, null=True)
  caption_url = models.CharField('Caption URL', max_length=255, blank=True, null=True)
  
  credit = models.CharField('Photo Credit', max_length=255, blank=True, null=True)
  credit_url = models.CharField('Photo Credit URL', max_length=255, blank=True, null=True)
  
  sorder = models.IntegerField('Order')
  
  def __unicode__ (self):
    return str(self.sorder)
    
  class Meta:
    ordering = ("sorder",)
    
  def file (self):
    return self.image.file
    
  def cap (self):
    if self.imageset.captype == 'mine' or self.caption:
      return self.caption
      
    return self.image.caption
    
  def cap_url (self):
    if self.imageset.captype == 'mine' or self.caption_url:
      return self.caption_url
    
    return self.image.caption_url
    
  def cred (self):
    if self.imageset.captype == 'mine' or self.credit:
      return self.credit
    
    return self.image.credit
    
  def cred_url (self):
    if self.imageset.captype == 'mine' or self.credit_url:
      return self.credit_url
      
    return self.image.credit_url
    
class Author (SitesMixin, models.Model):
  name = models.CharField(max_length=255)
  slug = models.SlugField(unique=True, max_length=200)
  email = models.EmailField(blank=True, null=True)
  
  image = models.ForeignKey(Image, blank=True, null=True)
  description = models.TextField('Description/Bio', blank=True, null=True)
  
  sites = models.ManyToManyField(Site, blank=True, null=True)
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "name__icontains")
    
  def __unicode__ (self):
    return self.name
    
  class Meta:
    ordering = ("name",)
    
  def Thumbnail (self):
    if self.image:
      return self.image.Thumbnail()
      
    return ''
    
  Thumbnail.allow_tags = True
  
TEMPLATES = []
for key, value in PIZZA_TEMPLATES.items():
  TEMPLATES.append((key, value['name']))
  
class Page (SitesMixin, models.Model):
  url = models.CharField('URL', max_length=255, help_text='Examples: / = HomePage, /some_page, /some_page/sub_page')
  tpl = models.CharField("Template", choices=TEMPLATES, max_length=255)
  
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
    
  def form_field (self, etype, name, initial=None):
    if etype == 'image':
      return forms.ModelChoiceField(
        queryset=Image.objects.all(),
        required=False, label=name,
        widget=ForeignKeyRawIdWidget(ManyToOneRel(Image, 'id'), admin.site),
        initial=initial
      )
      
    elif etype == 'rich':
      return forms.CharField(required=False, label=name, widget=RichText, initial=initial)
      
    elif etype == 'plain':
      return forms.CharField(required=False, label=name, widget=forms.Textarea, initial=initial)
      
    return forms.CharField(max_length=255, required=False, label=name, initial=initial, widget=forms.TextInput(attrs={'class': 'vTextField'}))
    
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
    for cvar, props in PIZZA_TEMPLATES[self.tpl]['regions'].items():
      initial = None
      if content.has_key(cvar):
        initial = content[cvar]
        
      fields['generatedfield_' + cvar] = self.form_field(*props, initial=initial)
      
    return type('AdminForm', (forms.ModelForm,), fields)
    
  def Versions (self):
    return '<div id="view_versions_%d"><a href="javascript: void(0);" onclick="get_versions(%d)">View Versions</a></div>' % (self.id, self.id)
    
  Versions.allow_tags = True
  
  def View_Published (self):
    edit_url = reverse('kitchen_sink:admin_editon')
    goto = urllib.quote('http://' + self.sites.all()[0].domain + self.url + '?preview=1')
    return '<a href="%s" target="_blank">View</a>&nbsp; -&nbsp;<a href="%s?goto=%s" target="_blank">Edit on Site</a>' % (self.url, edit_url, goto)
    
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
    for cvar, props in PIZZA_TEMPLATES[self.page.tpl]['regions'].items():
      if props[0] == 'image' and c.has_key(cvar) and c[cvar]:
        try:
          c[cvar] = Image.objects.get(id=c[cvar])
          
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
    