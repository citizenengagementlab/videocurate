from django.http import HttpResponse,HttpResponseRedirect,HttpResponseServerError,HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db.models import Q, Count
from django.contrib import messages
from datetime import datetime
from datetime import time
import dateutil.parser
import json
import urlparse

from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from embeds.models import SavedEmbed
from embeds.views import cache_embed
from tagging.models import Tag,TaggedItem
from tagging.utils import parse_tag_input
from mediacurate.models import Media,Location,Flag
from mediacurate.forms import AddForm

def home(request):
    if Media.objects.filter(featured=True).count() > 0:
        main = Media.objects.filter(featured=True).latest()
    else:
        try:
            main = Media.objects.order_by('-total_upvotes','-date_added')[0]
        except IndexError:
            #there's nothing in the db yet, render a blank page
            return render_to_response('view.html',
                   {'title':'The best source for #occupy videos',
                   'message':'Add some videos and start curating'},
                   context_instance=RequestContext(request))

    latest = Media.objects.order_by('-date_added').exclude(id=main.id)[:5]
    popular = Media.objects.order_by('-total_upvotes').exclude(id=main.id)[:5]
    
    tabs = [{'name':'Popular','list':popular,'view_all_link':'/popular/'},
            {'name':'Latest','list':latest,'view_all_link':'/latest/'}]
    
    return render_to_response('view.html',
        {'title':'Collaboratively Curated for the Movement',
        'banner':True,
        'media':main,'tabs':tabs},
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
    same_day = Media.objects.filter(date_uploaded__year=media.date_uploaded.year,
                                    date_uploaded__month=media.date_uploaded.month,
                                    date_uploaded__day=media.date_uploaded.day).order_by('-date_added').exclude(id=media.id)[:5]
    
    tabs = [{'name':'Nearby','list':nearby,'view_all_link':'/search?location=%s' % media.location.name},
            {'name':'Same Day','list':same_day,'view_all_link':'/search?date=%s' % media.date_uploaded.date()}]
    
    return render_to_response('view.html',
        {'media':media,'tabs':tabs},
        context_instance=RequestContext(request))
        
def view_inline(request,id,slug):
    try:
        media = Media.objects.get(id=id,slug=slug)
    except Media.DoesNotExist:
        media = get_object_or_404(Media,id=id)
    
    return render_to_response('view_inline.html',{'media':media},
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
                      'date':{'field':'date_uploaded','lookup':'__range'},
                      'url':{'field':'url','lookup':'__exact'}
                     }
    query = {} #will be passed to filter
    query_display = [] #for template display
    for (param,filters) in allowed_params.items():
        val = request.GET.get(param)
        if val:
            lookup_string = filters['field']+filters['lookup']
            if param == "date":
                #use range lookup, because django datetime is verbose
                try:
                    date = dateutil.parser.parse(val)
                except ValueError:
                   messages.error(request,"Couldn't determine a date from your query: "+val)
                   continue
                query[lookup_string] = (datetime.combine(date, time.min),
                                         datetime.combine(date, time.max))
            else:
                query[lookup_string] = val
            
            query_display.append("%s: %s" % (param,val))
            
    if len(query.keys()) == 0 and not request.GET.get('tag'):
        results = None
    else:
        results = Media.objects.filter(**query)
    
    #have to do tag searching outside of param loop, because it's not a Media field
    if request.GET.get('tag'):
        tag_name = request.GET.get('tag')
        tagged_ids = TaggedItem.objects.filter(tag__name=tag_name).values_list('object_id',flat=True)
        results = results.filter(id__in=tagged_ids)
        query_display.append("tagged: %s" % tag_name)
    
    return render_to_response('search.html',
        {'query':', '.join(query_display),'results':results},
        context_instance=RequestContext(request))

def location_autocomplete_list(request):
    #return list of locations in db, #occupy first
    try:
        query = request.GET['q']
    except KeyError:
        return HttpResponseBadRequest("need a query parameter")
    occupy_locations = Location.objects.filter(Q(name__istartswith="Occupy "+query)).values_list('name', flat=True)
    locations = Location.objects.filter(Q(name__istartswith=query)).values_list('name', flat=True)
    
    if len(occupy_locations) > 0:
        response_str = '\n'.join(occupy_locations) + '\n' + '\n'.join(locations)
    else:
        response_str = '\n'.join(locations)
    return HttpResponse(response_str, mimetype='text/plain')

def keywords(request):
    return render_to_response('tag_cloud.html',{},
        context_instance=RequestContext(request))
    
def latest(request):
    media_list = Media.objects.order_by('-date_added')
    paginator = Paginator(media_list, 20)
    
    page = request.GET.get('page')
    if not page:
        page = 1
    try:
        media_pages = paginator.page(page)
    except PageNotAnInteger:
        media_pages = paginator.page(1)
    except EmptyPage:
        media_pages = paginator.page(paginator.num_pages)    
        
    return render_to_response('search.html',
        {'query':'the latest','results':media_pages.object_list,
        'pagination':paginator,'page':media_pages},
        context_instance=RequestContext(request))
        
def popular(request):
    media_list = Media.objects.order_by('-total_upvotes')
    paginator = Paginator(media_list, 20)
    
    page = request.GET.get('page')
    if not page:
        page = 1
    try:
        media_pages = paginator.page(page)
    except PageNotAnInteger:
        media_pages = paginator.page(1)
    except EmptyPage:
        media_pages = paginator.page(paginator.num_pages)    
        
    return render_to_response('search.html',
        {'query':'the most popular','results':media_pages.object_list,
        'pagination':paginator,'page':media_pages},
        context_instance=RequestContext(request))

def locations(request):
    locations = Location.objects.annotate(num_media=Count('media')).filter(num_media__gt=0).order_by('name')
    
    return render_to_response('tiles.html',{'locations':locations},
        context_instance=RequestContext(request))

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
    if (parsed.netloc == "www.youtube.com"):
        qs = urlparse.parse_qs(parsed.query)
        if (qs.has_key('v') and len(qs['v'])>0):
            v = qs['v'][0]
        else:
            v = ""
        url = urlparse.urlunparse(('http', #ignore https
                                   parsed.netloc,
                                   parsed.path,
                                   parsed.params,
                                   'v='+v, #only save the video id
                                   parsed.fragment))
    if (parsed.netloc == "youtu.be"):
        #convert youtu.be to youtube url
        v = parsed.path[1:]
        url = urlparse.urlunparse(('http',
                                    'www.youtube.com',
                                    'watch',
                                    '',
                                    'v='+v,
                                    ''))
    #vimeo
        
    
    try:
        m = Media.objects.get(url=url)
        return HttpResponse(json.dumps({'exists':'true','local_url':m.get_absolute_url()}), mimetype="application/json")
    except Media.MultipleObjectsReturned:
        m = Media.objects.filter(url=url)
        first = m[0]
        return HttpResponse(json.dumps({'exists':'true','local_url':first.get_absolute_url()}), mimetype="application/json")
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
            provider_name = embed.get_response_dict()['provider_name']
            try:
                date_uploaded = dateutil.parser.parse(form.cleaned_data['date_uploaded']) #TEMP, may fail
            except ValueError,e:
                try:
                    date_uploaded = datetime.fromtimestamp(float(form.cleaned_data['date_uploaded']))
                except ValueError,e:
                    date_uploaded = datetime.now()
                    messages.debug("I don't know how to parse this date: %s from %s" % (form.cleaned_data['date_uploaded'],provider_name))
                
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
            }
            media = Media(**media_dict)
            media.save()
            #have to do this after first save, so we get an object_id
            Tag.objects.update_tags(media,form.cleaned_data['tags'])
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
                            
def add_tags(request,id):
    if request.method == "POST":
        m = get_object_or_404(Media,id=id)
        ctype = ContentType.objects.get_for_model(m)
        current_tags = Tag.objects.get_for_object(m)
        tags = parse_tag_input(request.POST.get('tags'))
    
        new_tags_list = []
        for t in tags:
            if t not in current_tags:
                tag,new_tag = Tag.objects.get_or_create(name=t)
                ti,new = TaggedItem.objects.get_or_create(tag=tag,content_type=ctype,object_id=m.pk)
                if new:
                    new_tags_list.append(t)

        return HttpResponse(json.dumps({'success':new_tags_list}), mimetype="application/json")
    else:
        return HttpResponse("POST a new tag")