from django.db import models
from jsonfield.fields import JSONField

OEMBED_TYPES = (
    ('video',)*2,
    ('photo',)*2,
    ('link',)*2,
    ('rich',)*2,
)

#class StoredProvider(models.Model):
#    name = models.CharField(max_length=255)
#    type = models.CharField(max_length=10, choices=OEMBED_TYPES)
#    domain = models.CharField(max_length=255)
#    favicon = models.URLField()
#    about = models.TextField()

class SavedEmbed(models.Model):
    url = models.URLField()
    maxwidth = models.SmallIntegerField(null=True, blank=True)
    type = models.CharField(max_length=10, choices=OEMBED_TYPES)
    response = JSONField(blank=True,help_text="stores the full embedly response, json formatted")
    html = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('url', 'maxwidth')

    def __unicode__(self):
        return self.url