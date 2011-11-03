from django import template
from mediacurate.models import Media,Location
from django.db.models import Count

register = template.Library()

@register.simple_tag
def current_location_count():
    return Location.objects.annotate(num_media=Count('media')).filter(num_media__gt=0).count()

@register.simple_tag
def current_media_count():
    return Media.objects.count()