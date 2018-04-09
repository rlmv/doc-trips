from django.contrib import admin

from fyt.applications.models import (
    CrooSupplement,
    LeaderSupplement,
    Volunteer
)

admin.site.register(Volunteer)
admin.site.register(CrooSupplement)
admin.site.register(LeaderSupplement)
