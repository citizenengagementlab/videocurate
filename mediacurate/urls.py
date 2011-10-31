from django.conf.urls.defaults import *

urlpatterns = patterns('mediacurate.views',
    (r'^$', 'home'),
    (r'^add/$', 'add'),
    (r'^search/$', 'search'),
    url(r'^view/(?P<id>[\d]+)/$', 'view_by_id', name='view_by_id'),
    url(r'^view/(?P<id>[\d]+)/(?P<slug>[\w-]+)/$', 'view_by_slug', name='view_by_slug'),
    url(r'^flag/(?P<id>[\d]+)/$', 'flag'),
    (r'^locations/','locations'),
    (r'^embed/cache', 'embed_cache'),
    
    #(r'^assignment/add/', 'assignment_add'),
    
    #autocomplete urls
    (r'^tags/', include('tagging_autocomplete.urls')),
    url(r'^locations/list/$', 'location_autocomplete_list', name="location_autocomplete_list"),
)

urlpatterns += patterns('secretballot.views',
    url(r'^view/vote/(?P<object_id>[\d]+)/(?P<vote>[-\d]+)/$', 'vote', kwargs={'content_type':'mediacurate.media',
                                                                            'mimetype':""}),
    url(r'^comment/vote/(?P<object_id>[\d]+)/(?P<vote>[-\d]+)/$', 'vote', kwargs={'content_type':'comments.comment',
                                                                            'mimetype':""}),
)