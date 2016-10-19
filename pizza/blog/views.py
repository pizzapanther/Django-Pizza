from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django import http
from django.conf import settings

from NextPlease import pagination

from .models import Blog, Post, Category

PIZZA_PODCAST_OWNER = getattr(settings, 'PIZZA_PODCAST_OWNER', 'John Doe')
PIZZA_PODCAST_OWNER_EMAIL = getattr(settings, 'PIZZA_PODCAST_OWNER_EMAIL', 'johndoe@example.com')
PIZZA_PODCAST_CATEGORY = getattr(settings, 'PIZZA_PODCAST_CATEGORY', 'Technology')
PIZZA_PODCAST_SUB_CATEGORY = getattr(settings, 'PIZZA_PODCAST_SUB_CATEGORY', 'Podcasting')

def blogs (request, filters={}):
  templates = ('blog/all.html', 'pizza/blog/all.html')
  
  c = {
    'blogs': Blog.objects.filter(**filters).filter(sites__id=request.pizza_site['id']),
  }
  return TemplateResponse(request, templates, c)
  
@pagination('posts')
def blog_index (request, slug=None, category=None, filters={}):
  blog = get_object_or_404(Blog, slug=slug, sites__id=request.pizza_site['id'], **filters)
  if category is not None:
    category = get_object_or_404(Category, slug=category)
    
  templates = ('blog/index.html', 'pizza/blog/index.html')
  mt = 'text/html'
  
  fmt = request.GET.get('format', '')
  ftype = request.GET.get('ftype', '')
  if fmt == 'atom':
    templates = ('blog/index.atom.xml', 'pizza/blog/index.atom.xml')
    mt = 'application/atom+xml'
    
  elif fmt == 'rss':
    templates = ('blog/index.rss.xml', 'pizza/blog/index.rss.xml')
    mt = 'application/rss+xml'
    
  elif fmt == 'podcast':
    templates = ('blog/itunes.xml', 'pizza/blog/itunes.xml')
    mt = 'application/rss+xml'
    
  c = {
    'blog': blog,
    'posts': blog.published(category, ftype),
    'category': category,
    'ftype': ftype,
    'ITUNES_OWNER': PIZZA_PODCAST_OWNER,
    'ITUNES_OWNER_EMAIL': PIZZA_PODCAST_OWNER_EMAIL,
    'ITUNES_CATEGORY': PIZZA_PODCAST_CATEGORY,
    'ITUNES_SUB_CATEGORY': PIZZA_PODCAST_SUB_CATEGORY,
  }
  return TemplateResponse(request, templates, c, content_type=mt)
  
def blog_detail (request, blog=None, slug=None, post=None):
  blog = get_object_or_404(Blog, slug=blog, sites__id=request.pizza_site['id'])
  if post:
    query = blog.published().filter(id=post)
    
  else:
    query = blog.published().filter(slug=slug)
    
  if query.count() == 0:
    raise http.Http404
    
  c = {
    'blog': blog,
    'post': query[0]
  }
  return TemplateResponse(request, ('blog/detail.html', 'pizza/blog/detail.html'), c)
  