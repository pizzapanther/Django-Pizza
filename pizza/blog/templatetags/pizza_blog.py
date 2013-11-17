from django import template

register = template.Library()


@register.filter
def get_file_format (post, ftype):
  return post.mediafile_set.get(ext__ext=ftype)
  
@register.filter
def http_url (url):
  return url.replace('https://', 'http://')
  