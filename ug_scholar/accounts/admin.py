from django.contrib import admin

from .models import User, UserLog

admin.site.register(User)
admin.site.register(UserLog)