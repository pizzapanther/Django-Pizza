from django.contrib import admin
from django.db import models
from django import forms

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
  
def merge_cats (modeladmin, request, queryset):
  if queryset.count() > 1:
    cat = queryset[0]
    for c in queryset[1:]:
      if hasattr(c, 'post_set'):
        for post in c.post_set.all():
          post.categories.remove(c)
          post.categories.add(cat)
          
      if hasattr(c, 'event_set'):
        for post in c.event_set.all():
          post.categories.remove(c)
          post.categories.add(cat)
          
    for c in queryset[1:]:
      c.delete()
      
merge_cats.short_description = "Merge Categories"

class CategoryAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'slug', 'posts')
  search_fields = ('title', 'slug')
  actions = (merge_cats,)
  
  def posts (self, obj):
    return obj.post_set.all().count()
    
class MediaFileInline (admin.TabularInline):
  model = MediaFile
  
class PostForm (forms.ModelForm):
  class Meta:
    model = Post
    fields = ('blog', 'title', 'slug', 'authors', 'categories', 'image', 'imageset', 'body',
              'audio_embed', 'video_embed', 'publish')
    widgets = {
      'body': RichText
    }
    
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
  
  form = PostForm
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
  list_display = ('title', 'ext', 'mtype')
  
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(FileFormat, FileFormatAdmin)
