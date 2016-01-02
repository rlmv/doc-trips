
from django.contrib import admin

from fyt.applications.models import GeneralApplication, CrooSupplement, LeaderSupplement, CrooApplicationGrade, LeaderApplicationGrade, QualificationTag, SkippedCrooGrade, SkippedLeaderGrade

admin.site.register(GeneralApplication)
admin.site.register(CrooSupplement)
admin.site.register(LeaderSupplement)
admin.site.register(CrooApplicationGrade)
admin.site.register(LeaderApplicationGrade)
admin.site.register(QualificationTag)
admin.site.register(SkippedCrooGrade)
admin.site.register(SkippedLeaderGrade)

