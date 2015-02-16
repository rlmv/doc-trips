
from django.contrib import admin

from applications.models import GeneralApplication, CrooSupplement, LeaderSupplement

admin.site.register(GeneralApplication)
admin.site.register(CrooSupplement)
admin.site.register(LeaderSupplement)

