from django.contrib import admin
from secretballot.models import *

class VoteAdmin(admin.ModelAdmin):
    list_display = ('date_added','vote','object_id')

admin.site.register(Vote,VoteAdmin)