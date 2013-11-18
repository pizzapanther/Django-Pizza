import json

from django.contrib import admin
from django.db import models
from django import forms
from django.conf import settings
from django.template.response import TemplateResponse
from django.contrib.sites.models import Site
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.db.models.fields.related import ManyToOneRel
from django.contrib.admin.util import unquote
from django.contrib.admin import helpers
from django.utils import timezone
from django import http
from django.contrib import messages

from .widgets import RichText
from .models import Page, Version, Redirect, Image, File, Blurb, Author, \
                    ImageSet, ImageSetItem, Inline, EDITORTYPES

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
    if hasattr(request, 'version') and request.version:
      return obj.admin_form(request.version)
      
    return super(PageAdmin, self).get_form(request, obj=obj, **kwargs)
    
  def get_object (self, request, object_id):
    request.version = None
    obj = super(PageAdmin, self).get_object(request, object_id)
    
    if request.GET.get('settings', '') != '1':
      ver = ''
      if request.method == 'GET':
        ver = request.GET.get('version', '')
        
      page = obj
      if ver:
        ret = page.version_set.get(id=ver)
        ret.publish = None
        request.version = ret
        return obj
        
      qs = page.version_set.filter(publish__isnull=True)
      if qs.count() > 0:
        request.version = qs[0]
        return obj
        
      else:
        qs = page.version_set.all()
        if qs.count() > 0:
          request.version = Version(
            page=qs[0].page,
            title=qs[0].title,
            keywords=qs[0].keywords,
            desc=qs[0].desc,
            content=qs[0].content
          )
          return obj
          
      request.version = Version(page=page)
      return obj
      
    return obj
    
  def get_urls (self):
    from django.conf.urls import patterns, url
    
    info = self.model._meta.app_label, self.model._meta.module_name
    urlpatterns = patterns('',
      url(r'^(.+)/versions/$', self.versionlist_view, name='%s_%s_versionlist' % info),
    )
    urlpatterns += super(PageAdmin, self).get_urls()
    
    return urlpatterns
    
  def versionlist_view (self, request, object_id):
    if not self.has_change_permission(request, None):
      raise PermissionDenied
      
    obj = self.get_object(request, object_id)
    return TemplateResponse(request, 'ks/admin_versions.html', {'page': obj})
    
  def save_model (self, request, obj, form, change):
    if hasattr(request, 'version') and request.version:
      cdict = {}
      for key in form.cleaned_data.keys():
        if key.startswith('generatedfield_'):
          if hasattr(form.cleaned_data[key], 'id'):
            cdict[key[15:]] = form.cleaned_data[key].id
            
          else:
            cdict[key[15:]] = form.cleaned_data[key]
            
      request.version.title = form.cleaned_data['title']
      request.version.keywords = form.cleaned_data['keywords']
      request.version.desc = form.cleaned_data['desc']
      if form.cleaned_data['publish_now']:
        request.version.publish = timezone.now()
        
      else:
        request.version.publish = form.cleaned_data['publish']
        
      request.version.set_content(cdict)
      request.version.save()
      
    else:
      super(PageAdmin, self).save_model(request, obj, form, change)
      
  def save_formset (self, request, form, formset, change):
    for f in formset:
      key = f.inline
      break
      
    cdict = request.version.get_content()
    cdict[key] = []
    instances = formset.save(commit=False)
    
    count = 0
    for inline in instances:
      d = {}
      for ikey, value in inline.cleaned_data.items():
        if ikey.startswith('generatedfield_'):
          if hasattr(value, 'id'):
            d[ikey[15:]] = value.id
            
          else:
            d[ikey[15:]] = value
            
      qs = Inline.objects.filter(page=request.version.page, icnt=count)
      if qs.count() == 0:
        iobj = Inline(page=request.version.page, icnt=count)
        iobj.save()
        
      else:
        iobj = qs[0]
        
      d['iid'] = iobj.id
      cdict[key].append(d)
      count += 1
      
    request.version.set_content(cdict)
    request.version.save()
    
  def get_inline_instances (self, request, obj=None):
    inline_instances = []
    if hasattr(request, 'version') and request.version:
      for inline_class in request.version.page.inlines(request.version):
        inline = inline_class(self.model, self.admin_site)
        inline_instances.append(inline)
        
    return inline_instances
    
  def change_view (self, request, object_id, form_url='', extra_context=None):
    publish_now = request.GET.get('publish_now', '')
    if publish_now == '1':
      page = self.get_object(request, unquote(object_id))
      version = page.version_set.get(publish__isnull=True)
      version.publish = timezone.now()
      version.save()
      self.message_user(request, '%s Published Successfully' % page.url, messages.SUCCESS)
      return http.HttpResponseRedirect('../')
      
    ret = super(PageAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)
    if request.method == 'GET' and isinstance(ret, TemplateResponse):
      if not ret.is_rendered:
        obj = self.get_object(request, unquote(object_id))
        ret.context_data['inline_admin_formsets'] = self.regenerate_inlines(request, obj)
        
    return ret
    
  def regenerate_inlines (self, request, obj):
    ModelForm = self.get_form(request, obj)
    formsets = []
    
    form = ModelForm(instance=obj)
    inline_instances = self.get_inline_instances(request, obj)
    prefixes = {}
    for FormSet, inline in zip(self.get_formsets(request, obj), inline_instances):
      prefix = FormSet.get_default_prefix()
      prefixes[prefix] = prefixes.get(prefix, 0) + 1
      if prefixes[prefix] != 1 or not prefix:
        prefix = "%s-%s" % (prefix, prefixes[prefix])
        
      init_post = {}
      count = 0
      for i, init in enumerate(inline.initial):
        param = '%s-%d-%s' % (prefix, i, 'id')
        if 'generatedfield_iid' in init:
          iobj = Inline.objects.get(id=init['generatedfield_iid'])
          del init['generatedfield_iid']
          init_post[param] = str(iobj.id)
          
          for k, value in init.items():
            param = '%s-%d-%s' % (prefix, i, k)
            init_post[param] = value
            
          count += 1
          
      extra = 0
      if inline.extra:
        icount = count
        while icount < inline.max_num and extra < inline.extra:
          if icount < inline.max_num  and extra < inline.extra:
            extra += 1
            icount += 1
            
          else:
            break
            
      init_post[prefix + '-TOTAL_FORMS'] = str(count + extra)
      init_post[prefix + '-INITIAL_FORMS'] = str(count)
      init_post[prefix + '-MAX_NUM_FORMS'] = str(inline.max_num)
      
      formset = FormSet(init_post, instance=obj, prefix=prefix, queryset=inline.queryset(request))
      formsets.append(formset)
      
    inline_admin_formsets = []
    for inline, formset in zip(inline_instances, formsets):
      fieldsets = list(inline.get_fieldsets(request, obj))
      readonly = list(inline.get_readonly_fields(request, obj))
      prepopulated = dict(inline.get_prepopulated_fields(request))
      
      inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
          fieldsets, prepopulated, readonly, model_admin=self)
          
      inline_admin_formsets.append(inline_admin_formset)
      
    return inline_admin_formsets
    
class ImageAdmin (admin.ModelAdmin):
  list_display = ('title', 'file', 'Thumbnail', 'view')
  search_fields = ('title', 'file')
  
  class Media:
    js = [] 
    for j in ADMIN_QUERY_JS:
      js.append(j)
      
    js.append('ks/js/admin_image.js')
    
  def url_view (self, request, object_id):
    obj = self.get_object(request, object_id)
    
    return http.HttpResponse(json.dumps({'url': obj.file.url}), content_type="application/json")
    
  def multi_view (self, request):
    if not self.has_add_permission(request):
      raise PermissionDenied
      
    model = self.model
    opts = model._meta
    
    c = {
      'title': 'Multi Image Upload',
      'app_label': opts.app_label,
      'opts': opts,
      'media': self.media,
      'add': True,
      'has_change_permission': True,
    }
    return TemplateResponse(request, 'ks/admin_multi_upload.html', c)
    
  def get_urls (self):
    from django.conf.urls import patterns, url
    
    info = self.model._meta.app_label, self.model._meta.module_name
    urlpatterns = patterns('',
      url(r'^multi/$', self.multi_view, name='%s_%s_multi' % info),
      url(r'^(.+)/get_url/$', self.url_view, name='%s_%s_url' % info),
    )
    urlpatterns += super(ImageAdmin, self).get_urls()
    
    return urlpatterns
    
class ImageSetItemInline (admin.StackedInline):
  model = ImageSetItem
  raw_id_fields = ('image',)
  autocomplete_lookup_fields = {
    'fk': ['image'],
  }
  
  fields = ('image', 'caption', 'caption_url', 'credit', 'credit_url', 'sorder')
  if 'grappelli' in settings.INSTALLED_APPS:
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
  
  def url_view (self, request, object_id):
    obj = self.get_object(request, object_id)
    
    return http.HttpResponse(json.dumps({'url': obj.file.url, 'title': obj.title}), content_type="application/json")
    
  def get_urls (self):
    from django.conf.urls import patterns, url
    
    info = self.model._meta.app_label, self.model._meta.module_name
    urlpatterns = patterns('',
      url(r'^(.+)/get_url/$', self.url_view, name='%s_%s_url' % info),
    )
    urlpatterns += super(FileAdmin, self).get_urls()
    
    return urlpatterns
    
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

