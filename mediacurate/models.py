from django.db import models
from django.contrib.localflavor.us.models import USStateField
from django_countries import CountryField
#from django.contrib.gis.db import models as geo_models
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from embeds.models import SavedEmbed
import tagging
from tagging.fields import TagField
import secretballot

from django.core.urlresolvers import reverse

class Location(models.Model):
    name = models.CharField(max_length=255)
    state = USStateField(null=True,blank=True)
    country = CountryField(null=True,blank=True)
    #dont require geodjango, use simple floats instead
    lat = models.FloatField(null=True,blank=True)
    lon = models.FloatField(null=True,blank=True)
    url = models.URLField(null=True,blank=True) #for occupy locations
    
    def __unicode__(self):
        return self.name
    
    # if we want to use geodjango, for more complicated queries like proximity
    # unncessecary for initial launch
#    latlon = geo_models.PointField(srid=4326)
#    objects = geo_models.GeoManager()

LICENSE_CHOICES = (
    ('CC','Creative Commons'),
    ('NONE','No restrictions'),
    ('PROP','Proprietary, no reuse allowed'),
    ('UNK','Unknown'),
)

class Media(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    date_uploaded = models.DateTimeField()
    title = models.CharField(max_length=100,db_index=True) #youtube limits to 100 characters
    slug = models.SlugField()
    location = models.ForeignKey(Location,db_index=True)
    
    url = models.URLField()
    embed = models.ForeignKey(SavedEmbed)
    resolution = models.CharField(help_text="maximum resolution as widthXheight",blank=True,null=True, max_length=10)
    
    author_name = models.CharField(max_length=100,blank=True,null=True)
    author_url = models.URLField(blank=True,null=True)
    license = models.CharField(choices = LICENSE_CHOICES, max_length=10, default="UNK")
    views = models.IntegerField(help_text="views at original provider",blank=True,null=True)
    
    featured = models.BooleanField(default=False,help_text="make this appear on the homepage")
    
    class Meta:
        verbose_name_plural = "Media"
        get_latest_by = 'date_added'

    def get_total_upvotes(self):
        #covenience method for admin, not sure why I have to do the queryset
        return Media.objects.get(id=self.id).total_upvotes
    get_total_upvotes.short_description = "Upfists"

    def is_highres(self):
        if self.resolution:
            w,h = self.resolution.split('x')
            if w > 640 and h > 480:
                return True
        return False
    def __unicode__(self):
        return "%s - %s @ %s" % (self.author_name,self.slug,self.location)
    def get_absolute_url(self):
        return reverse('view_by_slug',kwargs={'id':self.id,'slug':self.slug})
        
    def description(self):
        "Returns text of first comment, if available"
        content_type = ContentType.objects.get(app_label="mediacurate",model="media")
        comment_list = Comment.objects.filter(content_type=content_type,object_pk=self.pk).order_by('submit_date')
        if comment_list:
            c = comment_list[0]
            return '%s on %s: "%s"' % (c.name,c.submit_date.date(),c.comment)
        else:
            return None
            
tagging.register(Media,tag_descriptor_attr='tags')
secretballot.enable_voting_on(Media)
secretballot.enable_voting_on(Comment)
 
flag_reasons = (
    ('INAPP','Inappropriate'),
    ('OFFNS','Offensive'),
    ('SPAM','Spam'),
)
class Flag(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    media = models.ForeignKey(Media)
    reason = models.CharField(max_length=5,choices=flag_reasons)
    
    def __unicode__(self):
        return "%s - %s" % (self.get_reason_display(),self.media)

#class Assignment(models.Model):
#    date_added = models.DateTimeField(auto_now_add=True)
#    requester = models.ForeignKey(User) 
#    description = models.TextField()    
#    videos = models.ManyToManyField(Media)