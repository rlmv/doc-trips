

from django.contrib import admin

from leader.models import LeaderApplication, LeaderGrade

class LeaderGradeInline(admin.TabularInline):
    model = LeaderGrade
    
    readonly_fields = ['grader', 'grade', 'comment', 
                       'hard_skills', 'soft_skills']

    # see http://stackoverflow.com/a/19884095/3818777
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
        
class LeaderApplicationAdmin(admin.ModelAdmin):

    # can we hid trips_year? can we make trips_year universally uneditable/invisible?
    
    list_display = ('user', 'status')
    list_editable = ('status',)
    list_filter = ('status',)
    
 #   readonly_fields = [ 'trips_year',] # etc.

    inlines = [ LeaderGradeInline ]

#    change_list_template = "admin/change_list_filter_sidebar.html"
#    change_list_filter_template = "admin/filter_listing.html"

admin.site.register(LeaderApplication, LeaderApplicationAdmin)
admin.site.register(LeaderGrade)
