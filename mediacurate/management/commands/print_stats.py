from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.contrib.contenttypes.models import ContentType
from mediacurate.models import Media
from secretballot.models import Vote
from django.contrib.comments.models import Comment

import qsstats #http://pypi.python.org/pypi/django-qsstats-magic
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        #print visitor stats
        
        print "%d media uploaded" % Media.objects.all().count()
        
        media_type = ContentType.objects.get(app_label="mediacurate",model="media")
        votes = Vote.objects.filter(content_type=media_type)
        vote_ips = votes.values('token').distinct()
        print "%d votes from %d IPs" % (votes.count(), vote_ips.count())
        
        comments = Comment.objects.filter(content_type=media_type)
        comment_ips = comments.values('ip_address').distinct()
        print "%d comments from %d IPs" % (comments.count(), comment_ips.count())
        
        
        qss = qsstats.QuerySetStats(qs=Media.objects.all(),date_field='date_added')
        end = datetime.date.today() + datetime.timedelta(days=1) #fwd a day because the end date isn't inclusive
        start = datetime.date(2011,10,30) #site launch date
        results = qss.time_series(start,end,"days")
        print "\nUploads by date"
        for t in results:
            print "%s,%s" % (t[0].strftime('%x'),t[1])