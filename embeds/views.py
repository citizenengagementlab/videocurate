from django.http import HttpResponse,HttpResponseServerError,HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.cache import cache

import json
import re
from datetime import datetime
from hashlib import md5

from embedly import Embedly
from embeds.models import SavedEmbed

from embeds.templatetags.embed_filters import make_cache_key

USER_AGENT = 'Mozilla/5.0 (compatible; django-embedly/0.2; ' \
        '+http://github.com/BayCitizen/)'
        
def cache_embed(request,url,maxwidth):
    #try memcache first
    key = make_cache_key(url, maxwidth)
    cached_response = cache.get(key)
    if cached_response and type(cached_response) == type(dict()):    
        cached_response['cache'] = 'memcache'
        return HttpResponse(json.dumps(cached_response), mimetype="application/json")

    #then the database
    try:
        saved = SavedEmbed.objects.get(url=url, maxwidth=maxwidth)
        response = saved.get_response_dict()
        response['html'] = saved.html
        response['cache'] = 'database'
        cache.set(key, response) #and save it to memcache
        return HttpResponse(json.dumps(response), mimetype="application/json")
    except SavedEmbed.DoesNotExist:
        pass
    except TypeError:
        response = {'error':'Error embedding %s.' % url}
        return HttpResponseServerError(json.dumps(response), mimetype="application/json")
    except SyntaxError:
        #probably has old embed with no response
        saved.delete()
        saved.save()
        #clear it, so we don't get it from the cache again
        return HttpResponseServerError("no embed response for %s" % url)

    #if we've never seen it before, call the embedly API
    client = Embedly(key=settings.EMBEDLY_KEY, user_agent=USER_AGENT)
    if maxwidth:
       oembed = client.oembed(url, maxwidth=maxwidth)
    else:
       oembed = client.oembed(url)
    if oembed.error:
        print oembed.error
        response = {'error':'Error embedding %s' % url,'reason':oembed.error}
        return HttpResponseServerError(json.dumps(response), mimetype="application/json")

    #save result to database
    try:
        row = SavedEmbed.objects.get(url=url, maxwidth=maxwidth)
    except SavedEmbed.DoesNotExist:
        row = SavedEmbed()
        row.url = url
        row.maxwidth = maxwidth
        row.type=oembed.type
        row.provider_name=oembed.provider_name
        row.response=json.dumps(oembed.data)
        row.save()

    if oembed.type == 'photo':
        html = '<img src="%s" width="%s" height="%s" />' % (oembed.url,
               oembed.width, oembed.height)
    else:
        html = oembed.html

    if html:
        row.html = html
        row.last_updated = datetime.now()
        row.save()

    #and to memcache
    cache.set(key, row.response, 86400)
    response = row.response
    response['html'] = row.html #overwrite for custom oembed types
    response['cache'] = "none"
    return HttpResponse(json.dumps(response), mimetype="application/json")