from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import gdata.youtube.service
import urlparse

from mediacurate.models import Media

class Command(BaseCommand):
    #sync view counts and resolution with common embed providers
    #should probably be run nightly
    
    def handle(self, *args, **options):
        api = gdata.youtube.service.YouTubeService()
        num_saved = 0
        for m in Media.objects.all():
            if type(m.embed.response) == type(dict()) and m.embed.response.has_key('provider_name'):
                if m.embed.response['provider_name'] == "YouTube":
                    parsed = urlparse.urlparse(m.url)
                    qs = urlparse.parse_qs(parsed.query)
                    video_id = qs['v'][0]
                    try:
                        v = api.GetYouTubeVideoEntry(video_id=video_id)
                    except Exception,e:
                        print e
                        print "unable to get youtube data for video_id",video_id
                        print "original url",m.url
                        continue
                    
                    changed = False
                    
                    views = v.statistics.view_count
                    if views and (int(m.views) < int(views)):
                        print "updating views on",m.url,"from",m.views,"to",views
                        m.views = views
                        changed = True
                        #also try and get license, resolution
                    
                    if changed:
                        m.save()
                        num_saved += 1
                #vimeo, flickr
        print "updated stats for",num_saved,"media objects"