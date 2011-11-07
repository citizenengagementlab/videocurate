from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Count
from django.core import serializers
from tagging.models import Tag

def list_tags(request):
    try:
        q = request.GET['q']
    except KeyError:
        return HttpResponseBadRequest('need a query parameter')
    tags = Tag.objects.annotate(num_items=Count('items')).filter(num_items__gt=0).filter(name__istartswith=q)
    tags_list = tags.values_list('name', flat=True)

    return HttpResponse('\n'.join(tags_list), mimetype='text/plain')