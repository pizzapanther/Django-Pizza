from django.conf.urls import patterns, include, url

urlpatterns = patterns('pizza.calendar.views',
  url(r'^$', 'events', name='all'),
)