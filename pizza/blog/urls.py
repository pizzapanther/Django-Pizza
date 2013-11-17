from django.conf.urls import patterns, include, url

urlpatterns = patterns('pizza.blog.views',
  url(r'^$', 'blogs', name='blogs'),
  url(r'^(\S+)/$', 'blog_index', name='blog'),
)