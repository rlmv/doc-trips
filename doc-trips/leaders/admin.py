

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import mark_safe
from django.db import  models
from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from leaders.models import LeaderApplication, LeaderGrade, LeaderApplicationQuestion, LeaderApplicationAnswer


class LeaderGradeInline(admin.TabularInline):
    model = LeaderGrade

#    readonly_fields = ['grader', 'grade', 'comment',
#                       'hard_skills', 'soft_skills']

    # see http://stackoverflow.com/a/19884095/3818777
#    def has_delete_permission(self, request, obj=None):
#        return False
#    def has_add_permission(self, request, obj=None):
#        return False


class LeaderApplicationAdmin(admin.ModelAdmin):
    
    model = LeaderApplication
    inlines = [LeaderGradeInline]
    
class LeaderGradeAdmin(admin.ModelAdmin):

    model = LeaderGrade



admin.site.register(LeaderApplication, LeaderApplicationAdmin)
admin.site.register(LeaderGrade, LeaderGradeAdmin)
admin.site.register(LeaderApplicationQuestion)
admin.site.register(LeaderApplicationAnswer)
