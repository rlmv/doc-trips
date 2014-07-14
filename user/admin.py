from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from user.models import UserProfile

""" Display the UserProfile in the admin site. 

from http://stackoverflow.com/a/4565957/3818777
"""


class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline, ]

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
