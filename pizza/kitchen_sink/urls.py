from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
  url(r'^admin_editon/$', 'pizza.kitchen_sink.views.admin_editon', name='admin_editon'),
  
  url(r'^admin_image_list/$', 'pizza.kitchen_sink.views.admin_image_list', name='admin_image_list'),
  url(r'^admin_image_upload/$', 'pizza.kitchen_sink.views.admin_image_upload', name='admin_image_upload'),
)
