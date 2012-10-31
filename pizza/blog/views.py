from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django import http

from pizza.pagination import pagination

from .models import Blog, Post

@pagination('posts')
def blog_index (request, slug=None):
  blog = get_object_or_404(Blog, slug=slug, sites__id=request.pizza_site['id'])
  
  c = {
    'blog': blog,
    'posts': blog.published()
  }
  return TemplateResponse(request, ('blog/index.html', 'pizza/blog/index.html'), c)
  
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
  