import os
import re

from django import template

register = template.Library()

@register.filter
def get_file_format (post, ftype):
  return post.mediafile_set.get(ext__ext=ftype)
  
@register.filter
def http_url (url):
  return url.replace('https://', 'http://')
  
@register.filter
def filename (path):
  return os.path.basename(path)
  
@register.filter
def format_video_size (embed, size):
    size = size.split('x')
    
    embed = re.sub('width="\d+"', 'width="%s"' % size[0], embed, flags=re.I)
    embed = re.sub("width='\d+'", "width='%s'" % size[0], embed, flags=re.I)
    
    embed = re.sub('height="\d+"', 'height="%s"' % size[1], embed, flags=re.I)
    embed = re.sub("height='\d+'", "height='%s'" % size[1], embed, flags=re.I)
    
    return embed
    