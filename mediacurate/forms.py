from django import forms
from form_utils.forms import BetterForm
from tagging_autocomplete.widgets import TagAutocomplete
from mediacurate.widgets import LocationAutocomplete
from mediacurate.models import Media

class AddForm(BetterForm):
    '''Used on the add page. Includes first review.'''
    url = forms.URLField()
    title = forms.CharField()
    location = forms.CharField(widget=LocationAutocomplete)
    author_name = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}))
    #author_url = forms.CharField(widget=forms.widgets.HiddenInput())
    author_url = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}))
    
    name = forms.CharField(required=False)
    review = forms.CharField(widget=forms.widgets.Textarea(),required=False)
    tags = forms.CharField(widget=TagAutocomplete,required=False)
    
    date_uploaded = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    resolution = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    views = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    license = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    class Meta:
        fieldsets = (
            ('URL',{'fields':('url',),
                    'description':'Paste the URL to preview',
                    'classes':['']}
            ),
            ('Info',{'fields':('title','location','tags',),
                    'description':"Where was this taken, and what is it about?<br>These fields are required",
                    'classes':['']}
            ),
            ('More',{'fields':('name','review'),
                    'description':"Enter your review. This helps us categorize the content.<br>This is optional",
                    'classes':['review']}
            ),
            ('Metadata',{'fields':('author_name','author_url','resolution','views','license','date_uploaded'),
                    'description':"Extra data we could determine from the provider.<br>This is not editable",
                    'classes':['hidden']}
            ),
        )