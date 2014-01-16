import re
import datetime

import pytz
from dateutil.relativedelta import relativedelta

from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings

from .models import Event, Category

MONTHS = (
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
)

TZ = pytz.timezone(settings.TIME_ZONE)

def events (request):
  templates = ('calendar/events.html', 'pizza/calendar/events.html')
  
  kwargs = {}
  start = request.GET.get('start', '')
  category = request.GET.get('category', '')
  
  now = timezone.now()
  now = now.astimezone(TZ)
  today = datetime.datetime(now.year, now.month, now.day, tzinfo=TZ)
  
  kwargs['start_dt__gte'] = today
  
  #delta = datetime.timedelta(days=7)
  delta = relativedelta(months=1)
  
  if start:
    try:
      kwargs['start_dt__gte'] = datetime.datetime.strptime(start, '%m/%d/%Y')
      
    except:
      pass
      
  kwargs['start_dt__lt'] = kwargs['start_dt__gte'] + delta
  
  if category:
    try:
      category = Category.objects.get(slug=category)
      
    except:
      pass
      
    else:
      kwargs['categories'] = category
      
  events = Event.objects.filter(**kwargs)
  years = [kwargs['start_dt__gte'].year]
  months = MONTHS
  
  current_year = kwargs['start_dt__gte'].year
  while current_year >= now.year:
    if current_year != kwargs['start_dt__gte'].year:
      years.insert(0, current_year)
      
    current_year = current_year - 1
    
  current_year = kwargs['start_dt__gte'].year
  for i in range(1, 3):
    current_year += 1
    years.append(current_year)
    
  future_months = [now]
  for i in range(1, 12):
    future_months.append(now + relativedelta(months=i))
    
  c = {
    'events': events,
    'start': kwargs['start_dt__gte'],
    'next': kwargs['start_dt__lt'],
    'previous': kwargs['start_dt__gte'] - delta,
    'months': months,
    'years': years,
    'cats': Category.objects.all(),
    'category': category,
    'today': today,
    'future_months': future_months,
  }
  return TemplateResponse(request, templates, c)
  