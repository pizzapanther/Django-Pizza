from django.template.response import TemplateResponse

from pizza.pagination import pagination

@pagination('posts')
def blog_index (request, slug=None):
  return TemplateResponse(request, ['blog/index.html', 'pizza/blog/index.html'], {})
  