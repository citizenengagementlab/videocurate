from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

DEFAULT_VOTE_CHOICES = (
    (+1, '+1'),
    (-1, '-1'),
)

VOTE_CHOICES = getattr(settings, 'VOTE_CHOICES', DEFAULT_VOTE_CHOICES)

class Vote(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=50)
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    # generic foreign key to the model being voted upon
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('token', 'content_type', 'object_id'),)

    def __unicode__(self):
        return '%s from %s on %s' % (self.get_vote_display(), self.token,
                                     self.content_object)
