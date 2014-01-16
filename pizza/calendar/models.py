from django.db import models
from django.conf import settings
from django.utils import timezone
from django.template.defaultfilters import date

from pizza.kitchen_sink.models import SitesMixin, SlideshowMixin, CategoryAbstract

class Category (CategoryAbstract):
  pass
  
class Series (models.Model):
  title = models.CharField(max_length=255)
  
  class Meta:
    verbose_name_plural = 'Series'
    
  def __unicode__ (self):
    return self.title
    
  @staticmethod
  def autocomplete_search_fields ():
    return ("id__iexact", "title__icontains")
    
  def dates (self):
    dates = self.event_set.all()[:20].values_list('start_dt', flat=True)
    ret = ', '.join([date(d, settings.DATETIME_FORMAT) for d in dates])
    if self.event_set.all().count() > 20:
      ret += ' ... '
      ret += date(self.event_set.all().reverse()[0].start_dt, settings.DATETIME_FORMAT)
      
    return ret
    
class Event (SlideshowMixin, models.Model):
  title = models.CharField(max_length=255)
  
  start_dt = models.DateTimeField('Start')
  end_dt = models.DateTimeField('End', blank=True, null=True)
  all_day = models.BooleanField('All day event', default=False)
  
  url = models.URLField(blank=True, null=True)
  
  body = models.TextField()
  
  image = models.ForeignKey('kitchen_sink.Image', blank=True, null=True)
  imageset = models.ForeignKey('kitchen_sink.ImageSet', blank=True, null=True)
  
  series = models.ForeignKey(Series, blank=True, null=True)
  
  categories = models.ManyToManyField(Category, blank=True, null=True)
  
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "title__icontains")
    
  class Meta:
    ordering = ('start_dt', '-all_day', 'end_dt')
    
  def series_title (self):
    if self.series:
      return '%s&nbsp; -&nbsp; <a href="../series/%d/delete/">Delete Series</a>' % (self.series.title, self.series.id)
      
    return None
    
  series_title.allow_tags = True
  
  def __unicode__ (self):
    return '%s - %s' % (self.title, date(self.start_dt, settings.DATETIME_FORMAT))
    
  def Categories (self):
    ret = ''
    for c in self.categories.all():
      ret += c.title + ', '
      
    if ret:
      return ret[:-2]
      
    return ret
    
  def related (self, num=5):
    cats = self.categories.all()
    now = timezone.now()
    
    return Event.objects.filter(categories__in=cats, start_dt__gt=now).exclude(id=self.id).distinct()[:num]
    
  def dates_qs (self):
    return Event.objects.filter(series=self.series, start_dt__gte=self.start_dt)
    
  def dates (self, num=3):
    return self.dates_qs()[:num]
    