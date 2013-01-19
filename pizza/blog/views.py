from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django import http

from pizza.pagination import pagination

from .models import Blog, Post, Category

@pagination('posts')
def blog_index (request, slug=None, category=None):
  blog = get_object_or_404(Blog, slug=slug, sites__id=request.pizza_site['id'])
  if category is not None:
    category = get_object_or_404(Category, slug=category)
    
  templates = ('blog/index.html', 'pizza/blog/index.html')
  mt = 'text/html'
  
  fmt = request.GET.get('format', '')
  if fmt == 'atom':
    templates = ('blog/index.atom.xml', 'pizza/blog/index.atom.xml')
    mt = 'application/atom+xml'
    
  elif fmt == 'rss':
    templates = ('blog/index.rss.xml', 'pizza/blog/index.rss.xml')
    mt = 'application/rss+xml'
    
  c = {
    'blog': blog,
    'posts': blog.published(category),
    'category': category,
  }
  return TemplateResponse(request, templates, c, mimetype=mt)
  
def blog_detail (request, blog=None, slug=None, post=None):
  blog = get_object_or_404(Blog, slug=blog)
  query = blog.published().filter(id=post)
  if query.count() == 0:
    raise http.Http404
    
  c = {
    'blog': blog,
    'post': query[0]
  }
  return TemplateResponse(request, ('blog/detail.html', 'pizza/blog/detail.html'), c)
  