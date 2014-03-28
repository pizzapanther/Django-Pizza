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
from django.core.files.storage import get_storage_class
from django.utils import timezone

from .widgets import RichText, HiddenViewInput
from pizza.middleware import PIZZA_SITES_KEY, PIZZA_DEFAULT_SITE_KEY
from pizza.utils import cached_method, USING_GRAPPELLI

from sorl.thumbnail import get_thumbnail

PIZZA_FILE_DIR = getattr(settings, 'PIZZA_FILE_DIR', 'pizza/files/%Y-%m')
PIZZA_IMAGE_DIR = getattr(settings, 'PIZZA_IMAGE_DIR', 'pizza/images/%Y-%m')
PIZZA_TEMPLATES = getattr(settings, 'PIZZA_TEMPLATES', {})

def gen_path (instance, filename, base):
  sclass = get_storage_class()
  storage = sclass()
  
  while 1:
    path = timezone.now().strftime(base + '/%d%H%M%S%f_') + filename
    if not storage.exists(path):
      break
      
  return path
  
def file_path (instance, filename):
  return gen_path(instance, filename, PIZZA_FILE_DIR)
  
def image_path (instance, filename):
  return gen_path(instance, filename, PIZZA_IMAGE_DIR)
  
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
  file = models.FileField(upload_to=file_path)
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains", "file__icontains")
    
  def __unicode__ (self):
    return self.title
    
  class Meta:
    ordering = ("title",)
    
class Image (ViewFileMixin, models.Model):
  title = models.CharField(max_length=255)
  file = models.ImageField(upload_to=image_path)
  
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
    
  def jdict (self):
    return {
      'name': self.file.name,
      'url': self.file.url,
      'title': self.title,
      
      'caption': self.caption,
      'caption_url': self.caption_url,
      'credit': self.credit,
      'credit_url': self.credit_url,
    }
    
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
  
class ModelForm (forms.ModelForm):
  def save (self, *args, **kw):
    instance = super(ModelForm, self).save(*args, **kw)
    instance.cleaned_data = self.cleaned_data
    return instance
    
class CleanPublish (object):
  def clean_publish (self):
    data = self.cleaned_data['publish']
    if data:
      now = timezone.now()
      if data < now:
        raise forms.ValidationError("Publish must be in the future")
        
    return data
    
class Page (SitesMixin, models.Model):
  url = models.CharField('URL', max_length=255, help_text='Examples: / = HomePage, /some_page, /some_page/sub_page')
  tpl = models.CharField("Template", choices=TEMPLATES, max_length=255)
  
  sites = models.ManyToManyField(Site)
  
  class Meta:
    ordering = ('url',)
    
  def Url (self):
    return self.__unicode__()
    
  def __unicode__ (self):
    if self.url == '/':
      return '{ homepage }'
      
    return self.url
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "url__icontains",)
    
  def Settings (self):
    return '<a href="./%d/?settings=1">Edit Settings</a>' % self.id
    
  Settings.allow_tags = True
  
  def published_version (self, version=None):
    now = timezone.now()
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
    
  def form_field (self, etype, name, initial=None, req=False):
    field = models.ForeignKey(Image, blank=True, null=True)
    
    if etype == 'image':
      return forms.ModelChoiceField(
        queryset=Image.objects.all(),
        required=req, label=name,
        widget=ForeignKeyRawIdWidget(ManyToOneRel(field, Image, 'id', related_name='+'), admin.site),
        initial=initial
      )
      
    elif etype == 'rich':
      return forms.CharField(required=req, label=name, widget=RichText, initial=initial)
      
    elif etype == 'plain':
      return forms.CharField(required=req, label=name, widget=forms.Textarea, initial=initial)
      
    return forms.CharField(max_length=255, required=req, label=name, initial=initial, widget=forms.TextInput(attrs={'class': 'vTextField'}))
    
  def admin_form (self, version, regions=None, inline=None):
    if regions and inline:
      class Meta:
        model = Version
        exclude = ('page', 'content', 'title', 'keywords', 'desc', 'publish', 'version')
        
      fields = {
        'inline': inline,
        'Meta': Meta,
      }
      
      if USING_GRAPPELLI:
        fields['icnt'] = forms.IntegerField(widget=HiddenViewInput(), label="Order")
        
    else:
      class Meta:
        model = Version
        exclude = ('page', 'content')
        
      fields = {
        'title': forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'vTextField'}), initial=version.title),
        'keywords': forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'vTextField'}), initial=version.keywords),
        'desc': forms.CharField(max_length=255, label='Description', required=False, widget=forms.TextInput(attrs={'class': 'vTextField'}), initial=version.desc),
        'publish_now': forms.BooleanField(required=False, label='Publish Now'),
        'publish': forms.DateTimeField(required=False, widget=AdminSplitDateTime, label='Publish On'),
        
        'Meta': Meta,
      }
      
      regions = PIZZA_TEMPLATES[self.tpl]['regions']
      
    content = version.get_content()
    if inline:
      content = {}
      
    req = True
    for cvar, props in regions.items():
      initial = None
      if content.has_key(cvar):
        initial = content[cvar]
        
      fields['generatedfield_' + cvar] = self.form_field(*props, initial=initial, req=req)
      req = False
      
    if regions and inline:
      return type('AdminForm', (ModelForm,), fields)
      
    return type('AdminForm', (CleanPublish, ModelForm), fields)
    
  def inlines (self, version):
    classes = []
    if 'inlines' in PIZZA_TEMPLATES[self.tpl]:
      index = 0
      for key, inline in PIZZA_TEMPLATES[self.tpl]['inlines'].items():
        iclass = admin.StackedInline
        iextra = 3
        imax_num = None
        iname = None
        iplural = None
        
        if 'type' in inline and inline['type'] == 'table':
          iclass = admin.TabularInline
          
        if 'extra' in inline:
          iextra = inline['extra']
          
        if 'max_num' in inline:
          imax_num = inline['max_num']
          
        if 'verbose_name' in inline:
          iname = inline['verbose_name']
          
        if 'verbose_name_plural' in inline:
          iplural = inline['verbose_name_plural']
          
        init = []
        content = version.get_content()
        if key in content:
          init_list = content[key]
          for icnt, init_dict in enumerate(init_list):
            idict = {'icnt': icnt + 1}
            for ikey, value in init_dict.items():
              idict['generatedfield_' + ikey] = value
              
            init.append(idict)
            
        class AdminInline (iclass):
          extra = iextra
          max_num = imax_num
          model = Inline
          verbose_name = iname
          verbose_name_plural = iplural
          form = self.admin_form(version, regions=inline['regions'], inline=key)
          initial = init
          sortable_field_name = "icnt"
          
        classes.append(AdminInline)
        index += 1
        
    return classes
    
  def Versions (self):
    return """<div id="view_versions_%d">
      <a href="javascript: void(0);" onclick="get_versions(%d)">View Versions</a>
    </div>""" % (self.id, self.id)
    
  Versions.allow_tags = True
  
  def View_Published (self):
    edit_url = reverse('kitchen_sink:admin_editon')
    goto = urllib.quote('//' + self.domain() + self.url + '?preview=1')
    data = {'url': self.url, 'edit': edit_url, 'goto': goto, 'domain': self.domain()}
    return '<a href="//%(domain)s%(url)s" target="_blank">View</a>&nbsp; -&nbsp;<a href="%(edit)s?goto=%(goto)s" target="_blank">Edit on Site</a>' % data
    
  View_Published.allow_tags = True
  
  @cached_method
  def domain (self):
    if self.sites.all().count() > 0:
      return self.sites.all()[0].domain
      
    return ''
    
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
          
    if 'inlines' in PIZZA_TEMPLATES[self.page.tpl]:
      for inline, idict in PIZZA_TEMPLATES[self.page.tpl]['inlines'].items():
        if inline in c:
          for i in range(0, len(c[inline])):
            for cvar, props in idict['regions'].items():
              myc = c[inline][i]
              if props[0] == 'image' and myc.has_key(cvar) and myc[cvar]:
                try:
                  myc[cvar] = Image.objects.get(id=myc[cvar])
                  
                except models.ObjectDoesNotExist:
                  pass
                  
    return c
    
  def get_content (self):
    if self.content:
      return pickle.loads(str(self.content))
      
    return {}
    
  def set_content (self, d):
    self.content = pickle.dumps(d).decode('ascii', 'ignore')
    
  class Meta:
    ordering = ('-publish', 'id')
    
  def __unicode__ (self):
    return self.page.url
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains",)
    
class Inline (models.Model):
  page = models.ForeignKey(Page)
  icnt = models.IntegerField("Order")
  
  def __unicode__ (self):
    return ""
    
  class Meta:
    verbose_name = " "
    verbose_name_plural = " "
    ordering = ('icnt',)
    
class CategoryAbstract (models.Model):
  title = models.CharField(max_length=100)
  slug = models.SlugField(unique=True, max_length=200)
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains")
    
  class Meta:
    ordering = ('slug',)
    verbose_name_plural = 'Categories'
    abstract = True
    
  def __unicode__ (self):
    return self.title
    