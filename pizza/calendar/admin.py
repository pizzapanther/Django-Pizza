import pytz
import types
import datetime

from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
from django.utils.safestring import SafeText, mark_safe
from django.db.models import Count
from django.utils import timezone

from .models import Category, Event, Series
from pizza.utils import update_attrs, copy_inlines, copy_many_to_many, copy_model_instance
from pizza.blog.admin import CategoryAdmin
from pizza.kitchen_sink.admin import AdminMixin
from pizza.kitchen_sink.widgets import RichText

REPEAT_CHOICES = (
  ('none', 'None'),
  ('15', '15 Minutues'),
  ('30', 'Half Hour'),
  ('hour', 'Hourly'),
  ('day', 'Daily'),
  ('week', 'Weekly'),
  ('month_num', 'Monthly (Example: 3rd of every month)'),
  ('month', 'Monthly same day (Example: First Monday of the month)'),
  ('year', 'Yearly')
)

UPDATE_CHOICES = (
  ('me', 'Update just this event'),
  ('all', 'Update all events in series')
)

class EmptySeriesFilter (admin.SimpleListFilter):
  title = 'Empty Series'
  parameter_name = 'empty'
  
  def lookups (self, request, model_admin):
    return (('1', 'Empty'),)
    
  def queryset (self, request, queryset):
    if self.value() == '1':
      queryset = queryset.annotate(num_events=Count('event')).filter(num_events=0)
      
    return queryset
    
class SeriesAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'dates')
  list_filter = (EmptySeriesFilter,)
  search_fields = ('title',)
  
class EventForm (forms.ModelForm):
  repeat = forms.ChoiceField(choices=REPEAT_CHOICES, required=False)
  repeat_until = forms.DateTimeField(required=False, widget=widgets.AdminSplitDateTime())
  update = forms.ChoiceField(choices=UPDATE_CHOICES, initial="me", required=False)
  
  def clean (self):
    cleaned_data = super(EventForm, self).clean()
    if cleaned_data.get('repeat') and cleaned_data.get('repeat') != 'none':
      if cleaned_data.get('repeat_until'):
        if cleaned_data.get('start_dt') and cleaned_data.get('repeat_until') <= cleaned_data.get('start_dt'):
          self._errors["repeat_until"] = self.error_class(['Repeat Until must be after Start.'])
          
      else:
        self._errors["repeat_until"] = self.error_class(['Repeat Until required when repeating.'])
        
    if cleaned_data.get('start_dt') and cleaned_data.get('end_dt'):
      if cleaned_data.get('end_dt') <= cleaned_data.get('start_dt'):
        self._errors["end_dt"] = self.error_class(['End must be after Start.'])
        
    return cleaned_data
    
  class Meta:
    model = Event
    fields = ('title', 'start_dt', 'end_dt', 'all_day', 'body', 'image', 'imageset', 'categories', 'series')
    widgets = {
      'body': RichText
    }
    
class EventAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'start_dt', 'end_dt', 'all_day', 'Categories', 'series_title')
  list_filter = ('categories', 'all_day')
  search_fields = ('title', 'id')
  date_hierarchy = 'start_dt'
  
  raw_id_fields = ('image', 'imageset', 'series')
  autocomplete_lookup_fields = {
    'fk': ['series', 'image', 'imageset'],
  }
  filter_horizontal = ('categories',)
  
  form = EventForm
  
  fieldsets = (
    ('Update', {
      'fields': ('update',),
    }),
    
    ('Event Time', {
      'fields': ('start_dt', 'end_dt', 'all_day', 'series'),
    }),
    
    (None, {
      'fields': ('title', 'url', 'body', 'image', 'imageset', 'categories'),
    }),
  )
  
  fieldsets_add = (
    ('Event Time', {
      'fields': (
        'start_dt', 'end_dt', 'all_day',
        ('repeat', 'repeat_until'),
        'series'
      ),
    }),
    
    (None, {
      'fields': ('title', 'url', 'body', 'image', 'imageset', 'categories'),
    }),
  )
  
  def get_fieldsets (self, request, obj=None):
    if obj is None:
      return self.fieldsets_add
      
    return self.fieldsets
    
  def save_related (self, request, form, formsets, change):
    super(EventAdmin, self).save_related(request, form, formsets, change)
    
    if change:
      self.update_series(request, form.instance, form)
      
    else:
      self.save_new_series(request, form.instance, form)
      
  def update_series (self, request, obj, form):
    if form.cleaned_data.has_key('update') and form.cleaned_data['update'] == 'all':
      if obj.series:
        obj.series.title = obj.title
        obj.series.save()
        
        for updobj in obj.__class__.objects.filter(series=obj.series).exclude(id=obj.id):
          update_attrs(obj, updobj, ('start_dt', 'end_dt'))
          copy_many_to_many(obj, updobj)
          copy_inlines(obj, updobj)
          
  def save_new_series (self, request, obj, form):
    if form.cleaned_data.has_key('repeat') and form.cleaned_data['repeat'] != 'none':
      delta = None
      end_delta = None
      if obj.series is None:
        new_series = Series(title=obj.title)
        new_series.save()
        obj.series = new_series
        obj.save()
        
      if form['repeat'].data == '15':
        delta = datetime.timedelta(minutes=15)
        
      elif form['repeat'].data == '30':
        delta = datetime.timedelta(minutes=30)
        
      elif form['repeat'].data == 'hour':
        delta = datetime.timedelta(hours=1)
        
      elif form.cleaned_data['repeat'] == 'day':
        delta = datetime.timedelta(days=1)
        
      elif form.cleaned_data['repeat'] == 'week':
        delta = datetime.timedelta(days=7)
        
      elif form.cleaned_data['repeat'] == 'month':
        delta = datetime.timedelta(days=28)
        
      elif form.cleaned_data['repeat'] == 'month_num':
        delta = 'month'
        
      elif form.cleaned_data['repeat'] == 'year':
        delta = 'year'
        
      if obj.end_dt:
        end_delta = obj.end_dt - obj.start_dt
        
      if delta:
        start = obj.start_dt
        tz = timezone.get_current_timezone()
        old_dst = start.dst()
        
        while 1:
          if delta == 'year':
            start = start.replace(year=start.year + 1)
            
          elif delta == 'month':
            if start.month == 12:
              start = start.replace(year=start.year + 1, month=1)
              
            else:
              start = start.replace(month=start.month + 1)
            
          else:
            start += delta
            
          if start <= form.cleaned_data['repeat_until']:
            if tz.zone != 'UTC':
              start = tz.normalize(start)
              if old_dst != start.dst():
                start = start + (old_dst - start.dst())
                
            newobj = copy_model_instance(obj)
            newobj.start_dt = start
            
            if obj.end_dt:
              newobj.end_dt = newobj.start_dt + end_delta
              
            newobj.save()
            copy_many_to_many(obj, newobj)
            copy_inlines(obj, newobj)
            old_dst = start.dst()
            
          else:
            break
            
  def delete_view (self, request, object_id, extra_context=None):
    obj = self.get_object(request, object_id)
    series_id = None
    if obj and obj.series:
      series_id = obj.series.id
      
    ret = super(EventAdmin, self).delete_view(request, object_id, extra_context)
    
    if series_id and Event.objects.filter(series__id=series_id).count() == 0:
      Series.objects.get(id=series_id).delete()
      
    return ret
    
class EventCategoryAdmin (CategoryAdmin):
  list_display = ('title', 'slug', 'events')
  
  def events (self, obj):
    return obj.event_set.all().count()
    
admin.site.register(Category, EventCategoryAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Series, SeriesAdmin)
