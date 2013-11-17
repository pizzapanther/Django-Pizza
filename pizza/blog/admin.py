from django.contrib import admin
from django.db import models

from pizza.kitchen_sink.widgets import RichText
from pizza.kitchen_sink.admin import AdminMixin

from .models import Blog, Category, Post, FileFormat, MediaFile

import mpeg1audio

class BlogAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'slug', 'podcast', '_sites')
  search_fields = ('title', 'slug')
  list_filter = ('sites', 'podcast')
  filter_horizontal = ('sites', 'authors', 'formats')
  raw_id_fields = ('image',)
  autocomplete_lookup_fields = {
    'fk': ['image',],
  }
class CategoryAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'slug')
  search_fields = ('title', 'slug')
  
class MediaFileInline (admin.TabularInline):
  model = MediaFile
  
class PostAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'publish', 'slug', 'blog', 'Categories')
  search_fields = ('title', 'slug', 'blog')
  list_filter = ('blog', 'categories')
  date_hierarchy = 'publish'
  
  filter_horizontal = ('categories', 'authors')
  
  raw_id_fields = ('blog', 'image', 'imageset')
  autocomplete_lookup_fields = {
    'fk': ['blog', 'image', 'imageset'],
  }
  
  formfield_overrides = {
    models.TextField: {'widget': RichText},
  }
  
  inlines = (MediaFileInline,)
  
  def save_formset (self, request, form, formset, change):
    super(PostAdmin, self).save_formset(request, form, formset, change)
    
    for f in formset:
      if 'file' in f.cleaned_data and f.cleaned_data['file']:
        if f.cleaned_data['ext'].ext.lower() == 'mp3':
          f.cleaned_data['file'].seek(0)
          try:
            mp3 = mpeg1audio.MPEGAudio(f.cleaned_data['file'])
            
          except mpeg1audio.MPEGAudioHeaderException:
            pass
            
          else:
            f.instance.duration = mp3.duration
            f.instance.save()
            
          f.cleaned_data['file'].seek(0)
          
class FileFormatAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'ext')
  
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(FileFormat, FileFormatAdmin)
