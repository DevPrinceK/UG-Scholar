from django.contrib import admin

from .models import Author, Profile, Publication, SyncRun

admin.site.register(Publication)
admin.site.register(SyncRun)
admin.site.register(Profile)
admin.site.register(Author)
