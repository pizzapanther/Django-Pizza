import json
import types

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from django.utils import timezone

from pizza.kitchen_sink.models import Page, Version, Image, Inline

def yes_no (message):
  while 1:
    ans = raw_input(message + ' [y/n]: ')
    if ans.lower() in ['y', 'n']:
      if ans.lower() == 'y':
        return True
        
      break
      
  return False
  
def choose_page (page, pages):
  choices = {'0': None}
  print "Choose a page to overwrite for {} - {}".format(page['url'], page['sites_list'])
  print "0: Create New Page"
  
  count = 1
  for p in pages:
    choices[str(count)] = p
    sites = ", ".join(p.sites.all().values_list('name', flat=True))
    print "{}: {} - {}".format(count, p.url, sites)
    count += 1
    
  while 1:
    ans = raw_input('Choice: ')
    if ans in choices.keys():
      return choices[ans]
      
def new_version (page, **kwargs):
  v = kwargs['version']
  if v:
    version = Version(page=page,
      title=v['title'],
      keywords=v['keywords'],
      desc=v['description'],
    )
    
    if kwargs['published']:
      version.publish = timezone.now()
      
    del v['title']
    del v['keywords']
    del v['description']
    
    for key, value in v.items():
      if type(value) in [types.ListType, types.TupleType]:
        cnt = 0
        for item in value:
          inline = Inline(page=page, icnt=cnt)
          inline.save()
          item['iid'] = inline.id
          cnt += 1
          
    version.set_content(v)
    
    return version
    
  return None
  
def convert_images (vdict, create_images):
  for key, value in vdict.items():
    if type(value) is types.DictType:
      images = Image.objects.filter(file=value['name'])
      image = None
      
      if images.count() > 0:
        image = images[0]
        
      elif create_images:
        image = Image(file=value['name'])
        #todo check if image exists, if not download and add to storage
        
      if image:
        image.credit = value['credit']
        image.title = value['title']
        image.credit_url = value['credit_url']
        image.caption = value['caption']
        image.caption_url = value['caption_url']
        image.save()
        vdict[key] = image.id
        
      else:
        vdict[key] = image
        
    elif type(value) in [types.ListType, types.TupleType]:
      items = []
      for item in value:
        item = convert_images(item, create_images)
        items.append(item)
        
      vdict[key] = items
      
  return vdict
  
class Command (BaseCommand):
  args = '<json_file json_file ...>'
  help = 'Closes the specified poll for voting'
  
  def handle (self, *args, **options):
    create_sites = yes_no('Create Sites if not found?')
    create_images = yes_no('Create and download images?')
    
    for jfile in args:
      print 'Importing', jfile, '...'
      fh = open(jfile, 'r')
      data = json.loads(fh.read())
      fh.close()
      
      sites = {}
      for site in data['sites']:
        obj, created = Site.objects.get_or_create(name=site['name'], defaults={'domain': site['domain']})
        if created:
          if create_sites:
            print 'Created Site:', obj.name
            obj.save()
            
          else:
            obj = None
            
        sites[site['id']] = obj
        
      for export in data['exports']:
        export['sites_list'] = ", ".join([sites[s].name for s in export['sites']])
        
        pages = Page.objects.filter(url=export['url'])
        page = None
        if pages.count() == 1:
          page = pages[0]
          
        elif pages.count() > 1:
          page = choose_page(export, pages)
          
        if page is None:
          page = Page(url=export['url'], tpl='narf')
          
        print export['url'], '-', export['sites_list']
        page.tpl = export['tpl']
        page.save()
        page.sites.clear()
        for s in export['sites']:
          page.sites.add(sites[s])
          
        export['version'] = convert_images(export['version'], create_images)
        version = new_version(page, **export)
        if version:
          version.save()
          
      print 'Import Complete\n'
      