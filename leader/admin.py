

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import mark_safe
from django.db import  models
from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from leader.models import LeaderApplication, LeaderGrade


class LeaderGradeInline(admin.TabularInline):
    model = LeaderGrade
    
#    readonly_fields = ['grader', 'grade', 'comment', 
#                       'hard_skills', 'soft_skills']

    # see http://stackoverflow.com/a/19884095/3818777
#    def has_delete_permission(self, request, obj=None):
#        return False
#    def has_add_permission(self, request, obj=None):
#        return False


def add_link_field(target_model=None, field='', app='', field_name='link'):
    """ Decorator to add links to admin. 

    from http://stackoverflow.com/a/13287201/3818777 

    TODO: clean up, or use custom links per modeladmin.
    """
    
    def add_link(cls):
        reverse_name = target_model.lower() or cls.model.__name__.lower()

        def link(self, instance):
            app_name = app or instance._meta.app_label
            reverse_path = 'admin:{}_{}_change'.format(app_name, reverse_name)
            link_obj = getattr(instance, field, None) or instance
            url = reverse(reverse_path, args=(link_obj.id,))
            return mark_safe('<a href="{}">{}</a>'.format(url, link_obj))
        link.allow_tags = True
        link.short_description = reverse_name + ' link'

        setattr(cls, field_name, link)
        cls.readonly_fields = list(getattr(cls, 'readonly_fields', [])) + \
            [field_name]
        return cls
    return add_link

# TODO: link should land on trip display page, not scheduled trip change form
@add_link_field('ScheduledTrip', field='assigned_trip', app='trip', field_name='assigned_trip_link')
class LeaderApplicationAdmin(admin.ModelAdmin):

    # TODO: user should not be editable in change view
    
    list_display = ('user', 'class_year', 'status', 'assigned_trip','assigned_trip_link', 
                    'average_grade', 'grader_comments')
    list_display_links = ('user',)
    list_editable = ('status', 'assigned_trip')
    list_filter = ('status', 'class_year')

    # callables can only be displayed in 'fields' if they are readonly
    readonly_fields = ('average_grade', 'grader_comments') 
    fields = ('user', 
              ('status', 'average_grade', 'grader_comments'),
              ('assigned_trip', 'assigned_trip_link'),
              'class_year', 
              'tshirt_size', 
              'gender', 
              ('hinman_box', 'phone'),
              'offcampus_address',
              ('preferred_sections', 'available_sections'),
              'notes',
    )

    # show checkbox selectors for preferred_sections and available_sections 
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }

    inlines = [ LeaderGradeInline ]

    # grappelli options - show filters in the sidebar
    change_list_template = "admin/change_list_filter_sidebar.html"
    change_list_filter_template = "admin/filter_listing.html"


    def queryset(self, request):
        """ Compute the average value of all grades for application.
        
        This is saved on the model as grades__grade__avg. Objects are ordered
        by the computed averages. This overrides the default queryset method.
        """
        
        qs = super(LeaderApplicationAdmin, self).queryset(request)
        return qs.annotate(models.Avg('grades__grade')).order_by('grades__grade__avg')


    def average_grade(self, application):
        """ Get the average grade of application. 
        
        If not yet graded, return display placeholder.
        """
        
        avg = application.grades__grade__avg
        try:
            return round(avg, 1)
        except TypeError:
            return '-'
    average_grade.admin_order_field = 'grades__grade__avg'


    def grader_comments(self, application):
        
        return '<br/>'.join('{} - {}'.format(g.grade, g.comment) for g in application.grades.all())
    grader_comments.allow_tags = True



class LeaderGradeAdmin(admin.ModelAdmin):

    model = LeaderGrade
    
    

admin.site.register(LeaderApplication, LeaderApplicationAdmin)
admin.site.register(LeaderGrade, LeaderGradeAdmin)
