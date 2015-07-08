import csv
from collections import defaultdict

from braces.views import AllVerbsMixin
from vanilla import View, TemplateView
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.db.models import Avg

from doc.db.views import TripsYearMixin
from doc.applications.models import GeneralApplication as Application 
from doc.permissions.views import DatabaseReadPermissionRequired
from doc.incoming.models import Registration, IncomingStudent
from doc.core.models import Settings
from doc.utils.choices import YES, S, M, L, XL


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
        return Application.objects.leader_or_croo_applications(self.kwargs['trips_year'])

    def get_row(self, application):
        user = application.applicant
        return [user.name, application.class_year, user.netid]


class TripLeaderApplicationsCSV(GenericReportView):

    file_prefix = 'TL-applicants'
    header = ['name', 'class year', 'netid', 'avg score']
    
    def get_queryset(self):
        return (Application.objects
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
        return (Application.objects
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


class FinancialAidCSV(GenericReportView):

    file_prefix = 'Financial-aid'
    header = ['name', 'preferred name', 'netid', 'blitz', 'email']
    
    def get_queryset(self):
        return Registration.objects.want_financial_aid(self.get_trips_year())

    def get_row(self, reg):
        user = reg.user
        return [user.name, reg.name, user.netid, user.email, reg.email]


class ExternalBusCSV(GenericReportView):
    
    file_prefix = 'External-Bus-Requests'
    header = ['name', 'preferred_name', 'netid', 'requested stop', 'on route']
    
    def get_queryset(self):
        return Registration.objects.want_bus(self.get_trips_year())
        
    def get_row(self, reg):
        user = reg.user
        return [user.name, reg.name, user.netid, reg.bus_stop, reg.bus_stop.route]


class Charges(GenericReportView):
    """
    CSV file of charges to be applied to each trippee.
    """
    file_prefix = 'Charges'
    
    def get_queryset(self):
        return IncomingStudent.objects.filter(
            trips_year=self.get_trips_year(), trip_assignment__isnull=False
        )

    header = [
        'name', 'netid', 'total charge', 'aid award (percentage)',
        'bus', 'doc membership', 'green fund donation'
    ]
    def get_row(self, incoming):
        reg = incoming.get_registration()
        return [
            incoming.name,
            incoming.netid,
            incoming.compute_cost(),
            incoming.financial_aid if incoming.financial_aid != 0 else '',
            incoming.bus_assignment.cost if incoming.bus_assignment else '',
            self.membership_cost() if reg and reg.doc_membership == YES else '',
            reg.green_fund_donation if reg and reg.green_fund_donation else ''
        ]

    def membership_cost(self):
        return Settings.objects.get().doc_membership_cost


def tshirt_counts(trips_year):
    """
    Return a dict with S, M, L, XL keys, each
    with the number of shirts needed in that size.
    """
    counts = {S: 0, M: 0, L: 0, XL: 0}

    leaders = Application.objects.filter(
        trips_year=trips_year, status=Application.LEADER
    )
    croos = Application.objects.filter(
        trips_year=trips_year, status=Application.CROO
    )
    trippees = Registration.objects.filter(
        trips_year=trips_year
    )
    for qs in [leaders, croos, trippees]:
        for size in [S, M, L, XL]:
            counts[size] += qs.filter(tshirt_size=size).count()
    return counts


class TShirts(DatabaseReadPermissionRequired, TripsYearMixin, TemplateView):
    """
    Counts of all tshirt sizes requested by leaders, croos, and trippees.
    """
    template_name = "reports/tshirts.html"

    def get_context_data(self, **kwargs):
        kwargs['tshirt_counts'] = tshirt_counts(self.kwargs['trips_year'])
        return super(TShirts, self).get_context_data(**kwargs)


class Housing(GenericReportView):
    
    file_prefix = 'Housing'

    def get_queryset(self):
        return IncomingStudent.objects.filter(
            trips_year=self.kwargs['trips_year']
        )

    header = ['name', 'netid', 'trip', 'section', 'start date', 'end date']
    def get_row(self, incoming):
        is_assigned = incoming.trip_assignment is not None
        fmt = "%m/%d"
        return [
            incoming.name,
            incoming.netid,
            incoming.trip_assignment if is_assigned else "",
            incoming.trip_assignment.section.name if is_assigned else "",
            incoming.trip_assignment.section.trippees_arrive.strftime(fmt) if is_assigned else "",
            incoming.trip_assignment.section.return_to_campus.strftime(fmt) if is_assigned else "",
        ]
