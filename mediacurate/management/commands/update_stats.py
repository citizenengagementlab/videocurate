from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import gdata.youtube.service
import urlparse
import time

from django.conf import settings
from mediacurate.models import Media

class Command(BaseCommand):
    #sync view counts and resolution with common embed providers
    #should probably be run nightly
    
    def handle(self, *args, **options):
        try:
            api = gdata.youtube.service.YouTubeService(developer_key=settings.YOUTUBE_API_KEY)
        except AttributeError:
            print "no youtube api key, you are likely to get 403 errors"
            api = gdata.youtube.service.YouTubeService()
        num_saved = 0
        for m in Media.objects.all():
            if type(m.embed.response) == type(dict()) and m.embed.response.has_key('provider_name'):
                if m.embed.response['provider_name'] == "YouTube":
                    parsed = urlparse.urlparse(m.url)
                    qs = urlparse.parse_qs(parsed.query)
                    if qs.has_key('v'):
                        video_id = qs['v'][0]
                    else:
                        print "no video_id for",m.url
                        continue
                    try:
                        v = api.GetYouTubeVideoEntry(video_id=video_id)
                    except gdata.service.RequestError,inst:
                        error = inst[0]
                        if error['status'] == 403:
                            print "too many api requests, wait 10"
                            time.sleep(10)
                        else:
                            print error
                            print "unable to get youtube data for video_id",video_id
                            print "original url",m.url
                            continue
                    
                    changed = False
                    
                    views = v.statistics.view_count
                    change_views = False
                    if views and not m.views:
                        change_views = True
                    elif int(m.views) < int(views):
                        change_views = True
                    if change_views:
                        print "updating views on",m.url,"from",m.views,"to",views
                        m.views = views
                        changed = True
                        #also try and get license, resolution
                    
                    if changed:
                        m.save()
                        num_saved += 1
                time.sleep(0.5)
                #vimeo, flickr
        print "updated stats for",num_saved,"media objects"