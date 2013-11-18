from django.conf.urls import patterns, include, url

urlpatterns = patterns('pizza.blog.views',
  url(r'^$', 'blogs', name='all'),
  url(r'^(\S+)/category/(\S+)/$', 'blog_index', name='index-category'),
  url(r'^(\S+)/(\S+)/$', 'blog_detail', name='detail'),
  url(r'^(\S+)/$', 'blog_index', name='index'),
)