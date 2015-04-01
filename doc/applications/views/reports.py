import csv

from braces.views import AllVerbsMixin
from vanilla import View
from django.http import HttpResponse

from doc.db.views import TripsYearMixin
from doc.applications.models import GeneralApplication
from doc.permissions.views import DatabaseReadPermissionRequired


class VolunteerCSV(DatabaseReadPermissionRequired,
                   TripsYearMixin, AllVerbsMixin, View):

    def all(self, request, *args, **kwargs):
        trips_year = self.kwargs['trips_year']
        response = HttpResponse(content_type='text/csv')
        filename = 'TL-and-Croo-applicants-%s.csv' % trips_year
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        writer = csv.writer(response)
        qs = GeneralApplication.objects.leader_or_croo_applications(trips_year)
        for application in qs:
            user = application.applicant
            writer.writerow([user.name, user.netid])
        return response
