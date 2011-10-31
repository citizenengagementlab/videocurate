from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import urlparse

from mediacurate.models import Media

class Command(BaseCommand):
    #strip extra parameters from common sites to avoid duplicates
    
    def handle(self, *args, **options):
        num_changed = 0
        for m in Media.objects.all():
            parsed = urlparse.urlparse(m.url)
            #youtube
            if (parsed.netloc == "www.youtube.com") or (parsed.netloc == "youtu.be"):
                qs = urlparse.parse_qs(parsed.query)
                v = qs['v'][0]
                url = urlparse.urlunparse(('http', #ignore https
                                           parsed.netloc,
                                           parsed.path,
                                           parsed.params,
                                           'v='+v, #only save the video id
                                           parsed.fragment))
                #print "checking",m.url
                if m.url != url:
                    print "saving",url,"over",m.url
                    m.url = url
                    m.save()
                    num_changed += 1
        print "cleaned",num_changed,"urls"