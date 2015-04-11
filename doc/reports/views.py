import csv

from braces.views import AllVerbsMixin
from vanilla import View
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.db.models import Avg

from doc.db.views import TripsYearMixin
from doc.applications.models import GeneralApplication
from doc.permissions.views import DatabaseReadPermissionRequired


class GenericReportView(DatabaseReadPermissionRequired,
                        TripsYearMixin, AllVerbsMixin, View):
    
    file_prefix = None
    fieldnames = None
    
    def get_filename(self):
        return "{}-{}.csv".format(
            self.file_prefix, self.kwargs['trips_year']
        )
        
    def get_fieldnames(self):
        if self.fieldnames is not None:
            return self.fieldnames
        raise ImproperlyConfigured("add 'fieldnames' property")

    def get_queryset(self):
        raise ImproperlyConfigured('implement get_queryset()')

    def get_row(self, obj):
        raise ImproperlyConfigured('implement get_row()')

    def all(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="{}"'.format(self.get_filename())
        )
        writer = csv.DictWriter(response, fieldnames=self.get_fieldnames())
        writer.writeheader()
        for obj in self.get_queryset():
            writer.writerow(self.get_row(obj))
        return response


class VolunteerCSV(GenericReportView):

    file_prefix = 'TL-and-Croo-applicants'
    fieldnames = ['name', 'class year', 'netid']

    def get_queryset(self):
        return GeneralApplication.objects.leader_or_croo_applications(self.kwargs['trips_year'])

    def get_row(self, application):
        user = application.applicant
        return {'name': user.name, 
                'class year': application.class_year,
                'netid': user.netid}


class TripLeaderApplicationsCSV(GenericReportView):

    file_prefix = 'TL-applicants'
    fieldnames = ['name', 'class year', 'netid', 'avg score']
    
    def get_queryset(self):
        return (GeneralApplication.objects
                .leader_applications(self.kwargs['trips_year'])
                .annotate(avg_score=Avg('leader_supplement__grades__grade')))

    def get_row(self, application):
        user = application.applicant
        return {'name': user.name, 
                'class year': application.class_year,
                'netid': user.netid,
                'avg score': application.avg_score}

        
class CrooApplicationsCSV(GenericReportView):

    file_prefix = 'Croo-applicants'
    fieldnames = ['name', 'class year', 'netid', 'avg score']
    
    def get_queryset(self):
        return (GeneralApplication.objects
                .croo_applications(self.kwargs['trips_year'])
                .annotate(avg_score=Avg('croo_supplement__grades__grade')))

    def get_row(self, application):
        user = application.applicant
        return {'name': user.name,
                'class year': application.class_year,
                'netid': user.netid,
                'avg score': application.avg_score}
