from django.contrib import admin
from embeds.models import *

class EmbedAdmin(admin.ModelAdmin):
    list_display = ('url','type','last_updated')
    ordering = ('-last_updated',)

admin.site.register(SavedEmbed,EmbedAdmin)