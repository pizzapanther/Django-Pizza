from django.conf.urls import patterns, include, url

urlpatterns = patterns('pizza.blog.views',
  url(r'^$', 'blogs', name='all', kwargs={'filters': {'podcast': True}}),
  url(r'^(\S+)/category/(\S+)/$', 'blog_index', name='index-category', kwargs={'filters': {'podcast': True}}),
  url(r'^(\S+)/(\S+)/$', 'blog_detail', name='detail'),
  url(r'^(\S+)/$', 'blog_index', name='index', kwargs={'filters': {'podcast': True}}),
)