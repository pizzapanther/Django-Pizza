from django.template.response import TemplateResponse

def blog_index (request, slug=None):
  return TemplateResponse(request, ['blog/index.html', 'pizza/blog/index.html'], {})
  