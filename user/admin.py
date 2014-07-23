from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from user.models import UserProfile

""" Display the UserProfile in the admin site. 

from http://stackoverflow.com/a/4565957/3818777
"""

User = get_user_model()

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline, ]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_model_perms(self, request):
        return {}

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
