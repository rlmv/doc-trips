
from django.contrib import admin

from fyt.applications.models import (
    CrooApplicationGrade,
    CrooSupplement,
    Volunteer,
    LeaderApplicationGrade,
    LeaderSupplement,
    QualificationTag,
    SkippedCrooGrade,
    SkippedLeaderGrade,
)


admin.site.register(Volunteer)
admin.site.register(CrooSupplement)
admin.site.register(LeaderSupplement)
admin.site.register(CrooApplicationGrade)
admin.site.register(LeaderApplicationGrade)
admin.site.register(QualificationTag)
admin.site.register(SkippedCrooGrade)
admin.site.register(SkippedLeaderGrade)

