from django.contrib import admin
from django.db import models
from django import forms
from django.template.response import TemplateResponse
from django.contrib.sites.models import Site
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.db.models.fields.related import ManyToOneRel

from .widgets import RichText
from .models import Page, Version, Redirect, Image, File, Blurb, Author, \
                    ImageSet, ImageSetItem, EDITORTYPES

ADMIN_QUERY_JS = (
  'ks/js/jquery-1.8.0.min.js',
  'ks/js/clear_filters.js',
)

class AdminMixin (object):
  class Media:
    js = ADMIN_QUERY_JS
    
class AuthorAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('name', 'slug', 'Thumbnail', '_sites')
  search_fields = ('name', 'slug', 'description')
  raw_id_fields = ('image',)
  filter_horizontal = ('sites',)
  autocomplete_lookup_fields = {
    'fk': ['image'],
  }
  
  formfield_overrides = {
    models.TextField: {'widget': RichText},
  }
  
class ReAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('url', 'goto', '_sites')
  list_filter = ('sites',)
  search_fields = ('url', 'goto')
  filter_horizontal = ('sites',)
  
class PageAdmin (admin.ModelAdmin):
  list_display = ('url', 'tpl', '_sites', 'Settings', 'View_Published', 'Versions')
  list_filter = ('sites', 'tpl')
  search_fields = ('url',)
  filter_horizontal = ('sites',)
  
  class Media:
    css = {'all': ('ks/css/admin.css', )}
    js = (
      'ks/js/jquery-1.8.0.min.js',
      'ks/js/ks.js',
      'ks/js/clear_filters.js',
    )
    
  def get_form (self, request, obj=None, **kwargs):
    if obj and obj.__class__.__name__ == 'Version':
      return obj.page.admin_form(obj)
      
    return super(PageAdmin, self).get_form(request, obj=obj, **kwargs)
    
  def get_object (self, request, object_id):
    if request.GET.get('settings', '') != '1':
      ver = request.GET.get('version', '')
      page = super(PageAdmin, self).get_object(request, object_id)
      if ver:
        ret = page.version_set.get(id=ver)
        ret.publish = None
        return ret
        
      qs = page.version_set.filter(publish__isnull=True)
      if qs.count() > 0:
        return qs[0]
        
      else:
        qs = page.version_set.all()
        if qs.count() > 0:
          obj = Version(
            page=qs[0].page,
            title=qs[0].title,
            keywords=qs[0].keywords,
            desc=qs[0].desc,
            content=qs[0].content
          )
          return obj
          
      return Version(page=page)
      
    return super(PageAdmin, self).get_object(request, object_id)
    
  def response_change (self, request, obj):
    if obj and obj.__class__.__name__ == 'Version':
      obj = obj.page
      
    return super(PageAdmin, self).response_change(request, obj)
    
  def get_urls (self):
    from django.conf.urls import patterns, url
    
    info = self.model._meta.app_label, self.model._meta.module_name
    urlpatterns = patterns('', url(r'^(.+)/versions/$', self.versionlist_view, name='%s_%s_versionlist' % info),)
    urlpatterns += super(PageAdmin, self).get_urls()
    
    return urlpatterns
    
  def versionlist_view (self, request, object_id):
    if not self.has_change_permission(request, None):
      raise PermissionDenied
      
    obj = self.get_object(request, object_id)
    return TemplateResponse(request, 'ks/admin_versions.html', {'page': obj.page})
    
  def save_model (self, request, obj, form, change):
    if obj and obj.__class__.__name__ == 'Version':
      cdict = {}
      for key in form.cleaned_data.keys():
        if key.startswith('generatedfield_'):
          if hasattr(form.cleaned_data[key], 'id'):
            cdict[key[15:]] = form.cleaned_data[key].id
            
          else:
            cdict[key[15:]] = form.cleaned_data[key]
            
      obj.set_content(cdict)
      
    return super(PageAdmin, self).save_model(request, obj, form, change)
    
class ImageAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'file', 'Thumbnail', 'view')
  search_fields = ('title', 'file')
  
class ImageSetItemInline (admin.StackedInline):
  model = ImageSetItem
  raw_id_fields = ('image',)
  autocomplete_lookup_fields = {
    'fk': ['image'],
  }
  
  fields = ('image', 'caption', 'caption_url', 'credit', 'credit_url', 'sorder')
  sortable_field_name = "sorder"
  formfield_overrides = {
    models.IntegerField: {'widget': forms.HiddenInput},
  }
  
class ImageSetAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'Thumbnails')
  search_fields = ('title',)
  inlines = (ImageSetItemInline,)
  
class FileAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'file')
  search_fields = ('title', 'file')
  
class BlurbAdmin (AdminMixin, admin.ModelAdmin):
  list_display = ('title', 'slug', 'etype', 'Settings')
  search_fields = ('title', 'slug')
  list_filter = ('etype',)
  #formfield_overrides = {
  #  models.TextField: {'widget': RichText},
  #}
  
  def form_field (self, etype, initial=None):
    if etype == 'image':
      return forms.ModelChoiceField(
        queryset=Image.objects.all(),
        required=False, label='Content',
        widget=ForeignKeyRawIdWidget(ManyToOneRel(Image, 'id'), admin.site),
        initial=initial
      )
      
    elif etype == 'rich':
      return forms.CharField(required=False, label='Content', widget=RichText, initial=initial)
      
    elif etype == 'plain':
      return forms.CharField(required=False, label='Content', widget=forms.Textarea, initial=initial)
      
    return forms.CharField(max_length=255, required=False, label='Content', initial=initial, widget=forms.TextInput(attrs={'class': 'vTextField'}))
    
  def edit_form (self, obj):
    class Meta:
      model = Blurb
      fields = ('title', 'content')
      
    fields = {
      'title': forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'vTextField', 'readonly': 'readonly'})),
      'content': self.form_field(obj.etype),
      
      'Meta': Meta
    }
    return type('AdminForm', (forms.ModelForm,), fields)
    
  def setting_form (self):
    class Meta:
      model = Blurb
      fields = ('title', 'slug', 'etype')
      
    fields = {
      'title': forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'vTextField'})),
      'slug': forms.SlugField(widget=forms.TextInput(attrs={'class': 'vTextField'})),
      'etype': forms.ChoiceField(label="Content Type", choices=EDITORTYPES),
      
      'Meta': Meta
    }
    return type('AdminForm', (forms.ModelForm,), fields)
    
  def get_form (self, request, obj=None, **kwargs):
    if obj is None or request.GET.get('settings', '') == '1':
      return self.setting_form()
      
    return self.edit_form(obj)
    
admin.site.register(Author, AuthorAdmin)
admin.site.register(Redirect, ReAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(ImageSet, ImageSetAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Blurb, BlurbAdmin)

