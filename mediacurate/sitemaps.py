from django.contrib.sitemaps import Sitemap
from django.db.models import Count
from mediacurate.models import Media, Location

class MediaSitemap(Sitemap):
    def items(self):
        return Media.objects.all()
    def lastmod(self, obj):
        return obj.date_added
        
class LocationSitemap(Sitemap):
    def items(self):
        return Location.objects.annotate(num_media=Count('media')).filter(num_media__gt=0)
        