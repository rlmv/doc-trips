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
    header = None
    
    def get_filename(self):
        return "{}-{}.csv".format(
            self.file_prefix, self.kwargs['trips_year']
        )
        
    def get_header(self):
        if self.header is not None:
            return self.header
        raise ImproperlyConfigured("add 'header' property")

    def get_queryset(self):
        raise ImproperlyConfigured('implement get_queryset()')

    def get_row(self, obj):
        raise ImproperlyConfigured('implement get_row()')

    def all(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="{}"'.format(self.get_filename())
        )
        writer = csv.writer(response)
        writer.writerow(self.get_header())
        for obj in self.get_queryset():
            writer.writerow(self.get_row(obj))
        return response


class VolunteerCSV(GenericReportView):

    file_prefix = 'TL-and-Croo-applicants'
    header = ['name', 'class year', 'netid']

    def get_queryset(self):
        return GeneralApplication.objects.leader_or_croo_applications(self.kwargs['trips_year'])

    def get_row(self, application):
        user = application.applicant
        return [user.name, application.class_year, user.netid]


class TripLeaderApplicationsCSV(GenericReportView):

    file_prefix = 'TL-applicants'
    header = ['name', 'class year', 'netid', 'avg score']
    
    def get_queryset(self):
        return (GeneralApplication.objects
                .leader_applications(self.kwargs['trips_year'])
                .annotate(avg_score=Avg('leader_supplement__grades__grade'))
                .select_related('leader_supplement')
                .prefetch_related('leader_supplement__grades'))

    def get_row(self, application):
        user = application.applicant
        if application.avg_score:
            avg_score = "%.1f" % application.avg_score
        else:
            avg_score = None
        row = [user.name, application.class_year,
               user.netid, avg_score]
        return row + [grade.grade for grade in
                      application.leader_supplement.grades.all()]


class CrooApplicationsCSV(GenericReportView):

    file_prefix = 'Croo-applicants'
    header = ['name', 'class year', 'netid', 'avg score']
    
    def get_queryset(self):
        return (GeneralApplication.objects
                .croo_applications(self.kwargs['trips_year'])
                .annotate(avg_score=Avg('croo_supplement__grades__grade'))
                .select_related('croo_supplement')
                .prefetch_related('croo_supplement__grades'))

    def get_row(self, application):
        user = application.applicant
        if application.avg_score:
            avg_score = "%.1f" % application.avg_score
        else:
            avg_score = None
        row = [user.name, application.class_year,
               user.netid, avg_score]
        return row + [grade.grade for grade in
                      application.croo_supplement.grades.all()]
