from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.contrib.contenttypes.models import ContentType
from mediacurate.models import Media
from secretballot.models import Vote
from django.contrib.comments.models import Comment


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