from django.conf.urls.defaults import *

urlpatterns = patterns('embeds.views',
    (r'^cache/', 'cache_embed'),
)
