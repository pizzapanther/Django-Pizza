from django.contrib import admin
from django.template.response import TemplateResponse
from django.contrib.sites.models import Site

from .models import Page, Version, Redirect, Template, TemplateRegion, Image, File

class ReAdmin (admin.ModelAdmin):
  list_display = ('url', 'goto', '_sites')
  list_filter = ('sites',)
  search_fields = ('url', 'goto')
  
class PageAdmin (admin.ModelAdmin):
  list_display = ('url', 'template', '_sites', 'Settings', 'View_Published', 'Versions')
  list_filter = ('sites', 'template')
  search_fields = ('url',)
  
  class Media:
    css = {'all': ('ks/redactor/admin.css', )}
    js = (
      'ks/js/jquery-1.8.0.min.js',
      'ks/js/ks.js',
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
    
class RegionInline (admin.TabularInline):
  model = TemplateRegion
  
class TemplateAdmin (admin.ModelAdmin):
  list_display = ('name', 'template')
  inlines = (RegionInline,)
  
class ImageAdmin (admin.ModelAdmin):
  list_display = ('title', 'file', 'Thumbnail', 'added_by', 'view')
  list_filter = ('added_by',)
  search_fields = ('title', 'file')
  exclude = ('added_by',)
  
  def save_model (self, request, obj, form, change):
    obj.added_by = request.user
    return super(ImageAdmin, self).save_model(request, obj, form, change)
    
class FileAdmin (admin.ModelAdmin):
  list_display = ('title', 'file', 'added_by')
  list_filter = ('added_by',)
  search_fields = ('title', 'file')
  exclude = ('added_by',)
  
  def save_model (self, request, obj, form, change):
    obj.added_by = request.user
    return super(FileAdmin, self).save_model(request, obj, form, change)
    
admin.site.register(Redirect, ReAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(File, FileAdmin)
