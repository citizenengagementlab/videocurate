from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import gdata.youtube.service
import urlparse
import datetime
import dateutil.parser
import pytz
import time

from django.conf import settings
from mediacurate.models import Media,SavedEmbed

class Command(BaseCommand):
    #sync view counts and resolution with common embed providers
    #should probably be run nightly
    
    def handle(self, *args, **options):
        print "updating statistics @",datetime.datetime.now()
        try:
            api = gdata.youtube.service.YouTubeService(developer_key=settings.YOUTUBE_API_KEY)
        except AttributeError:
            print "no youtube api key, you are likely to get 403 errors"
            api = gdata.youtube.service.YouTubeService()
        num_saved = 0
        for m in Media.objects.all():
            embed_response = m.embed.get_response_dict()
            if embed_response['provider_name']:
                provider = embed_response['provider_name']
            else:
                print "cannot determine provider for",m
                continue
                
            if provider == "YouTube":
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
                        print "unable to get youtube data for video_id",video_id,"url",m.url
                        continue
            
                changed = False
            
                #view count
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
            
                #date published, because I screwed up in the original add_media.js
                date_published_text = v.published.text
                date_published = dateutil.parser.parse(date_published_text)
                
                date_uploaded = m.date_uploaded.replace(tzinfo=pytz.utc)
                #get offset-aware version
                
                change_date = False
                if date_published and not date_uploaded:
                    change_date = True
                if date_published != date_uploaded:
                    change_date = True
                if change_date:
                    print "updating date published on",m.url,"from",m.date_uploaded,"to",date_published
                    m.date_uploaded = date_published
                    changed = True
            
                if changed:
                    m.save()
                    num_saved += 1
            time.sleep(0.25)
            #vimeo, flickr
        print "updated stats for",num_saved,"media objects"