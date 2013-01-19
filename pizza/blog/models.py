from django.db import models
from django.contrib.sites.models import Site

from pizza.kitchen_sink.models import SitesMixin, SlideshowMixin
from pizza.utils import now

class Blog (SitesMixin, models.Model):
  title = models.CharField(max_length=255)
  slug = models.SlugField(unique=True, max_length=200)
  description = models.TextField()
  
  authors = models.ManyToManyField('kitchen_sink.Author', blank=True, null=True)
  
  sites = models.ManyToManyField(Site, blank=True, null=True)
  
  def published (self, category=None):
    if category:
      return self.post_set.filter(publish__lte=now(), categories=category)
      
    return self.post_set.filter(publish__lte=now())
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains")
    
  def __unicode__ (self):
    return self.title
    
  class Meta:
    ordering = ('title',)
    
class Category (models.Model):
  title = models.CharField(max_length=100)
  slug = models.SlugField(unique=True, max_length=200)
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains")
    
  class Meta:
    ordering = ('slug',)
    verbose_name_plural = 'Categories'
    
  def __unicode__ (self):
    return self.title
    
class Post (SlideshowMixin, models.Model):
  blog = models.ForeignKey(Blog)
  
  title = models.CharField(max_length=255)
  slug = models.SlugField(unique=True, max_length=200)
  author = models.ForeignKey('kitchen_sink.Author')
  publish = models.DateTimeField()
  categories = models.ManyToManyField(Category, blank=True, null=True)
  
  body = models.TextField()
  
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
    