from django.http import HttpResponse,HttpResponseRedirect,HttpResponseServerError,HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db.models import Q, Count
from django.contrib import messages
from datetime import datetime
import dateutil.parser
import json
import urlparse,copy

from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from embeds.models import SavedEmbed
from embeds.views import cache_embed
from mediacurate.models import Media,Location,Flag
from mediacurate.forms import AddForm

def home(request):
    if Media.objects.filter(featured=True).count() > 0:
        main = Media.objects.filter(featured=True).latest()
    else:
        try:
            main = Media.objects.order_by('total_upvotes','date_added')[0]
        except IndexError:
            #there's nothing in the db yet, render a blank page
            return render_to_response('view.html',
                   {'title':'The best source for #occupy videos',
                   'message':'Add some videos and start curating'},
                   context_instance=RequestContext(request))

    latest = Media.objects.order_by('-date_added').exclude(id=main.id)[:5]
    popular = Media.objects.order_by('total_upvotes').exclude(id=main.id)[:5]
    
    stats = {'media_count':Media.objects.count(),
            'location_count':Location.objects.annotate(num_media=Count('media')).filter(num_media__gt=0).count()}
    
    tabs = [{'name':'Latest','list':latest},
            {'name':'Popular','list':popular},]
    
    return render_to_response('view.html',
        {'title':'The best source for #occupy videos',
        'media':main,'tabs':tabs,'stats':stats},
        context_instance=RequestContext(request))

def view_by_id(request,id):
    media = get_object_or_404(Media,id=id)
    return HttpResponseRedirect(media.get_absolute_url())

def view_by_slug(request,id,slug):
    try:
        media = Media.objects.get(id=id,slug=slug)
    except Media.DoesNotExist:
        media = get_object_or_404(Media,id=id)
    
    nearby = Media.objects.filter(location=media.location).order_by('-date_added').exclude(id=media.id)[:5]
    same_day = Media.objects.filter(date_uploaded=media.date_uploaded).order_by('-date_added').exclude(id=media.id)[:5]
    
    stats = {'media_count':Media.objects.count(),
            'location_count':Location.objects.annotate(num_media=Count('media')).filter(num_media__gt=0).count()}
    tabs = [{'name':'Nearby','list':nearby,'link':'/search?'},
            {'name':'Same Day','list':same_day,'link':'/search?'}]
    
    return render_to_response('view.html',
        {'media':media,'tabs':tabs,'stats':stats},
        context_instance=RequestContext(request))

#@require_POST
def flag(request,id):
    if not request.GET.get('reason'):
        return HttpResponseBadRequest('reason is required')
    try:
        media = Media.objects.get(id=id)
    except Media.DoesNotExist:
        return HttpResponseBadRequest("no media with that id")
    flag = Flag(media=media,reason=request.GET.get('reason'))
    flag.save()
    return HttpResponse('flagged!');

def search(request):
    #simple search
    #TODO: look into using haystack or django-filter
    allowed_params = {'keyword':{'field':'title','lookup':'__icontains'},
                      'location':{'field':'location__name','lookup':'__startswith'},
                      'tag':{'field':'tags','lookup':'__icontains'},
                      'date':{'field':'date_uploaded','lookup':''},
                      'url':{'field':'url','lookup':'__exact'}
                     }
    query = {} #will be passed to filter
    query_display = [] #for template display
    for (param,filters) in allowed_params.items():
        if request.GET.get(param):
            val = request.GET.get(param)
            lookup_string = filters['field']+filters['lookup']
            query[lookup_string] = val
            
            query_display.append("%s: %s" % (param,val))
    if len(query.keys()) == 0:
        #so we don't return all items
        results = None
    else:
        results = Media.objects.filter(**query)
    
    return render_to_response('search.html',
        {'query':', '.join(query_display),'results':results},
        context_instance=RequestContext(request))

def location_autocomplete_list(request):
    #return list of locations in db, #occupy first
    query = request.GET['q']
    occupy_locations = Location.objects.filter(Q(name__istartswith="Occupy "+query)).values_list('name', flat=True)
    locations = Location.objects.filter(Q(name__istartswith=query)).values_list('name', flat=True)
    
    if len(occupy_locations) > 0:
        response_str = '\n'.join(occupy_locations) + '\n' + '\n'.join(locations)
    else:
        response_str = '\n'.join(locations)
    return HttpResponse(response_str, mimetype='text/plain')

def embed_cache(request):
    #check if the url is already a media object first, before hitting embeds for it
    if not request.POST:
        return HttpResponseBadRequest("check_exists requires POST")
    url = request.POST.get('url')
    if not url:
        return HttpResponseBadRequest("POST a url, and I'll happily check for it")
    
    #strip extra parameters from common sites to avoid duplicates
    parsed = urlparse.urlparse(url)
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
    #vimeo
        
    
    try:
        m = Media.objects.get(url=url)
        print "exists"
        return HttpResponse(json.dumps({'exists':'true'}), mimetype="application/json")
    except Media.DoesNotExist:
        return cache_embed(request,url,request.POST.get('maxwidth'))
    
def add(request):
    form = AddForm()
    message = None
    if request.method == "POST":
        form = AddForm(request.POST)
        if form.is_valid():
            #first, check to see if it already exists
            try:
                exists = Media.objects.get(url=form.cleaned_data['url'])
                messages.info(request, "Thanks for adding that video. It's so good, we already have a copy. Want to add your review and tags?")
                #redirect, so we can clear url parameters
                return HttpResponseRedirect(exists.get_absolute_url())
            except Media.DoesNotExist:
                #it's new, continue with the form
                pass
            
            #create the objects with form.cleaned_data
            #can't use form.save() here, because it's not a modelform...
            
            location,new = Location.objects.get_or_create(name=form.cleaned_data['location'])
            embed = SavedEmbed.objects.get(url=form.cleaned_data['url'])
            
            #TODO: convert date_uploaded to consistent format
            provider_name = embed.response['provider_name']
            try:
                date_uploaded = dateutil.parser.parse(form.cleaned_data['date_uploaded']) #TEMP, may fail
            except ValueError,e:
                return HttpResponseServerError("I don't know how to parse this date:",form.cleaned_data['date_uploaded'],"from",provider_name)
                
            #could start with copy of form.cleaned_data, but that would pull in shared form fields
            media_dict = {
                'date_uploaded':date_uploaded,
                'title':form.cleaned_data['title'],
                'slug':slugify(form.cleaned_data['title'])[:50],
                'location':location,
                'url':form.cleaned_data['url'],
                'embed':embed,
                'resolution':form.cleaned_data['resolution'],
                'author_name':form.cleaned_data['author_name'],
                'author_url':form.cleaned_data['author_url'],
                'license':form.cleaned_data['license'],
                'views':form.cleaned_data['views'],
                'tags':form.cleaned_data['tags'],
            }
            media = Media(**media_dict)
            media.save()
            
            if form.cleaned_data['review']:
                comment_dict = {
                    'user_name':form.cleaned_data['name'],
                    'comment':form.cleaned_data['review'],
                    'submit_date':datetime.now(),
                    'ip_address':request.META['REMOTE_ADDR'],
                    'content_type':ContentType.objects.get(app_label="mediacurate",model="media"),
                    'object_pk':media.pk,
                    'site_id':1 #assuming we're only using one site
                }
                review = Comment(**comment_dict)
                review.save()
            messages.success(request, "Thanks for adding <a href='%s'>%s</a>. Want to add another?" % (media.get_absolute_url(), media.title))
            #redirect, so we can clear url parameters
            return HttpResponseRedirect('/add')
    return render_to_response('add.html',
                            {'form':form,
                            'message':message},
                            context_instance=RequestContext(request))