from django.contrib import admin
from mediacurate.models import *

class MediaAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_uploaded'
    ordering = ('date_added',)
    raw_id_fields = ('embed',)
    
    list_display = ('title','location','date_uploaded','date_added','resolution','get_total_upvotes','featured')
    list_filter = ('date_uploaded','location','featured')
    search_fields = ('title','location__name','tags')
    fieldsets = (
        ('Site',{'fields':('title','slug','location','tags')}),
        ('Host',{'fields':('url','embed','date_uploaded','resolution','license','views')}),
    )

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name','state','country','url')
    list_filter = ('state','country')
    ordering = ('state',)
    search_fields = ('name',)
    
class FlagAdmin(admin.ModelAdmin):
    list_display = ('reason','media','date_added')

admin.site.register(Media,MediaAdmin)
admin.site.register(Location,LocationAdmin)
admin.site.register(Flag,FlagAdmin)