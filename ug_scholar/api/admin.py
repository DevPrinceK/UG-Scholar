from django.contrib import admin

from .models import Author, Profile, Publication

admin.site.register(Publication)
admin.site.register(Profile)
admin.site.register(Author)
