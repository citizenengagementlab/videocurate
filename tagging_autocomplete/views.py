from django.http import HttpResponse
from django.db.models import Count
from django.core import serializers
from tagging.models import Tag

def list_tags(request):
	try:
		tags = Tag.objects.annotate(num_items=Count('items')).filter(num_items__gt=0).filter(name__istartswith=request.GET['q'])
		tags_list = tags.values_list('name', flat=True)
	except KeyError:
		pass
	
	return HttpResponse('\n'.join(tags_list), mimetype='text/plain')