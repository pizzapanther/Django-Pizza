import os
import mimetypes

mimetypes.init()

from django.db import models
from django.contrib.sites.models import Site
from django.utils import timezone
from django.conf import settings

from pizza.kitchen_sink.models import SitesMixin, SlideshowMixin, CategoryAbstract
from pizza.utils import now, cached_method

PIZZA_MEDIA_DIR = getattr(settings, 'PIZZA_MEDIA_DIR', 'pizza/media/%Y-%m')

def file_path (instance, filename):
  path = timezone.now().strftime(PIZZA_MEDIA_DIR)
  path = os.path.join(path, instance.post.slug + '.' + instance.ext.ext)
  
  return path
  
class FileFormat (models.Model):
  title = models.CharField(max_length=255)
  ext = models.SlugField('File Extension', max_length=10, help_text='Ex: mp3, m4v, etc')
  mtype = models.CharField('Media Type', max_length=25, choices=(('audio', 'Audio'), ('video', 'Video')))
  
  class Meta:
    ordering = ('title',)
    
  def __unicode__ (self):
    return self.title
    
class Blog (SitesMixin, models.Model):
  title = models.CharField(max_length=255)
  slug = models.SlugField(unique=True, max_length=200)
  description = models.TextField()
  image = models.ForeignKey('kitchen_sink.Image', blank=True, null=True)
  podcast = models.BooleanField(default=False)
  
  authors = models.ManyToManyField('kitchen_sink.Author', blank=True, null=True)
  
  sites = models.ManyToManyField(Site, blank=True, null=True)
  
  formats = models.ManyToManyField(FileFormat, blank=True, null=True)
  
  @cached_method
  def categories (self):
    return Category.objects.filter(post__blog=self).distinct()
    
  def published (self, category=None, ftype=None):
    qs = self.post_set.filter(publish__lte=now())
    if category:
      qs = self.post_set.filter(publish__lte=now(), categories=category)
      
    if ftype:
      qs = qs.filter(mediafile__ext__ext=ftype)
      
    return qs
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains")
    
  def __unicode__ (self):
    return self.title
    
  class Meta:
    ordering = ('title',)
    
class Category (CategoryAbstract):
  pass
  
class Post (SlideshowMixin, models.Model):
  blog = models.ForeignKey(Blog)
  
  title = models.CharField(max_length=255)
  slug = models.SlugField(unique=True, max_length=200)
  authors = models.ManyToManyField('kitchen_sink.Author', blank=True, null=True)
  publish = models.DateTimeField()
  categories = models.ManyToManyField(Category, blank=True, null=True)
  
  body = models.TextField()
  audio_embed = models.TextField('Audio Embed Code', blank=True, null=True)
  video_embed = models.TextField('Video Embed Code', blank=True, null=True)
  
  image = models.ForeignKey('kitchen_sink.Image', blank=True, null=True)
  imageset = models.ForeignKey('kitchen_sink.ImageSet', blank=True, null=True)
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains", "slug__icontains")
    
  class Meta:
    ordering = ('-publish',)
    
  def __unicode__ (self):
    return self.title
    
  def Categories (self):
    ret = ''
    for c in self.categories.all():
      ret += c.title + ', '
      
    if ret:
      return ret[:-2]
      
    return ret
    
  def related (self, num=5):
    cats = self.categories.all()
    return Post.objects.filter(categories__in=cats).exclude(id=self.id).distinct()[:num]
    
class MediaFile (models.Model):
  file = models.FileField(upload_to=file_path)
  ext = models.ForeignKey(FileFormat)
  post = models.ForeignKey(Post)
  duration = models.CharField(max_length=25, help_text='hh:mm:ss', blank=True, null=True)
  
  def __unicode__ (self):
    return self.file.name
    
  def mimetype (self):
    mtype, encoding = mimetypes.guess_type(self.file.name)
    if not mtype:
      mtype = 'application/octet-stream'
      
    return mtype
    