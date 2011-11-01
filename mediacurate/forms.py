from django import forms
from form_utils.forms import BetterForm
from django.contrib.comments.forms import CommentDetailsForm
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.conf import settings
import datetime

from tagging_autocomplete.widgets import TagAutocomplete
from mediacurate.widgets import LocationAutocomplete
from mediacurate.models import Media

class AddForm(BetterForm):
    '''Used on the add page. Includes first review.'''
    url = forms.URLField()
    title = forms.CharField(help_text="If the current title is confusing or not descriptive, please edit it. Context is key.",
        error_messages={'required':'A title is required.'})
    location = forms.CharField(widget=LocationAutocomplete,
        error_messages={'required':'Please enter a location.'},
        help_text="Where did this happen? City name or Occupy location first. <a href='#' id='no_location'>No location?</a>")
    author_name = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}))
    #author_url = forms.CharField(widget=forms.widgets.HiddenInput())
    author_url = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}))
    
    name = forms.CharField(required=False,help_text="Tell us who you are, so commenters can follow the discussion.")
    review = forms.CharField(widget=forms.widgets.Textarea(),required=False,help_text="The more information you provide, the more useful it is to others. What made you want to add this to the collection? Is there a particularly good portion that viewers should watch out for?")
    tags = forms.CharField(widget=TagAutocomplete,required=True,help_text="Use existing tags before creating new ones, they will autocomplete as you type.")
    
    date_uploaded = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    resolution = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    views = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    license = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    class Meta:
        fieldsets = (
            ('URL',{'fields':('url',),
                    'description':'Paste <a id="provider_link" href="http://embed.ly/providers" title="Can be YouTube, Vimeo, Flickr, or over 200 others" target="_blank">almost any URL</a> to preview.',
                    'classes':['url']}
            ),
            ('Basic Information <b>(Required)</b>',{'fields':('title','location','tags',),
                    'description':"Where was this taken, and what is it about?",
                    'classes':['basic']}
            ),
            ('Data <b>(Not Editable)</b>',{'fields':('author_name','author_url','resolution','views','license','date_uploaded'),
                    'description':"This is information we pull from the host site.",
                    'classes':['hidden']}
            ),
            ('Review <b>(Optional)</b>',{'fields':('name','review'),
                    'description':"Please enter a review. It helps others to know what to look for, and helps us categorize the content.",
                    'classes':['review']}
            ),
        )
    
    def clean(self):
        "If comment added, name required."
        cleaned_data = self.cleaned_data
        name = cleaned_data.get("name")
        review = cleaned_data.get("review")

        if review and not name:
            msg = u"If leaving a review, a name is required"
            self._errors["name"] = self.error_class([msg])
            del cleaned_data["name"]
        if name and not review:
            msg = "Do you want to enter a review now?"
            self._errors["review"] = self.error_class([msg])
            del cleaned_data["review"]
            
        return cleaned_data

class SlimCommentForm(CommentDetailsForm):
    def get_comment_create_data(self):
           """
           Subclass of contrib comment details form, but without email or url
           """
           return dict(
               content_type = ContentType.objects.get_for_model(self.target_object),
               object_pk    = force_unicode(self.target_object._get_pk_val()),
               user_name    = self.cleaned_data["name"],
              # user_email   = self.cleaned_data["email"],
              # user_url     = self.cleaned_data["url"],
               comment      = self.cleaned_data["comment"],
               submit_date  = datetime.datetime.now(),
               site_id      = settings.SITE_ID,
               is_public    = True,
               is_removed   = False,
           )