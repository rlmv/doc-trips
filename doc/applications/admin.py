
from django.contrib import admin

from doc.applications.models import GeneralApplication, CrooSupplement, LeaderSupplement, CrooApplicationGrade, LeaderApplicationGrade

admin.site.register(GeneralApplication)
admin.site.register(CrooSupplement)
admin.site.register(LeaderSupplement) 
admin.site.register(CrooApplicationGrade)
admin.site.register(LeaderApplicationGrade)

