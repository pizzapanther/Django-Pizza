from django.contrib import admin
from django.db import models

from pizza.kitchen_sink.widgets import RichText
from pizza.kitchen_sink.admin import AdminMixin

from .models import Blog, Category, Post

class BlogAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'slug', '_sites')
  search_fields = ('title', 'slug')
  list_filter = ('sites',)
  filter_horizontal = ('sites', 'authors')
  
class CategoryAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'slug')
  search_fields = ('title', 'slug')
  
class PostAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'publish', 'slug', 'blog', 'Categories')
  search_fields = ('title', 'slug', 'blog')
  list_filter = ('blog', 'categories')
  date_hierarchy = 'publish'
  
  filter_horizontal = ('categories',)
  
  raw_id_fields = ('blog', 'author', 'image', 'imageset')
  autocomplete_lookup_fields = {
    'fk': ['blog', 'author', 'image', 'imageset'],
  }
  
  formfield_overrides = {
    models.TextField: {'widget': RichText},
  }
  
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
