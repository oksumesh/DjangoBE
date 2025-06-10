from django.contrib import admin
from .models import Poll, Option, Vote, UserProfile

admin.site.register(Poll)
admin.site.register(Option)
admin.site.register(Vote)
admin.site.register(UserProfile)
