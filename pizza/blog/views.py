from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404

from pizza.pagination import pagination

from .models import Blog

@pagination('posts')
def blog_index (request, slug=None):
  blog = get_object_or_404(Blog, slug=slug, sites__id=request.pizza_site['id'])
  
  c = {
    'blog': blog,
    'posts': blog.published()
  }
  return TemplateResponse(request, ('blog/index.html', 'pizza/blog/index.html'), c)
  