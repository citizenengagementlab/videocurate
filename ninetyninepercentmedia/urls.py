from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps import FlatPageSitemap
from mediacurate.sitemaps import MediaSitemap,LocationSitemap

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/tag_cleanup/', include('django_antichaos.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^', include('mediacurate.urls')),
)

sitemaps = {
    'flatpages': FlatPageSitemap,
    'media': MediaSitemap,
    'locations':LocationSitemap,
}
urlpatterns += patterns('',
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})
)

#debug media server
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
    )