import csv
from collections import OrderedDict

from braces.views import AllVerbsMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q, Avg, Count, Max, Prefetch
from django.http import HttpResponse
from django.utils.functional import cached_property
from vanilla import View

from fyt.applications.models import Volunteer as Application
from fyt.applications.views.application import preload_questions
from fyt.db.views import DatabaseTemplateView, TripsYearMixin
from fyt.incoming.models import (
    IncomingStudent,
    Registration,
    RegistrationSectionChoice,
    RegistrationTripTypeChoice,
    Settings,
)
from fyt.permissions.views import DatabaseReadPermissionRequired
from fyt.trips.models import Section, Trip, TripType
from fyt.utils.cache import cache_as
from fyt.utils.choices import TSHIRT_SIZES


def yes_no(value):
    return 'yes' if value else 'no'


def yes_if_true(value):
    return 'yes' if value else ''


def fmt_float(value):
    if value is None:
        return ''
    return '{:.1f}'.format(value)


class GenericReportView(DatabaseReadPermissionRequired,
                        TripsYearMixin, AllVerbsMixin, View):
    # TODO use a ListView here?

    file_prefix = None
    header = None

    def get_filename(self):
        return "{}-{}.csv".format(
            self.file_prefix, self.get_trips_year()
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
    header = [
        'name',
        'netid',
        'avg score',
        'status',
        'leader app',
        'croo app',
        'class year',
        'gender',
        'race/ethnicity',
        'hometown',
        'clubs/interests',
        'co-leader',
    ]

    def get_header(self):
        score_count_max = Application.objects.leader_or_croo_applications(
            trips_year=self.get_trips_year()
        ).annotate(
            Count('scores')
        ).aggregate(
            Max('scores__count')
        )['scores__count__max']

        return self.header + ['score {}'.format(i)
                              for i in range(1, score_count_max + 1)]

    def get_queryset(self):
        qs = Application.objects.leader_or_croo_applications(
            trips_year=self.get_trips_year()
        ).annotate(
            avg_score=Avg('scores__score')
        ).prefetch_related(
            'scores'
        )
        return preload_questions(qs, self.get_trips_year())

    def get_row(self, application):
        user = application.applicant
        return [
            user.name,
            user.netid,
            fmt_float(application.avg_score),
            application.status,
            yes_no(application.leader_application_complete),
            yes_no(application.croo_application_complete),
            application.class_year,
            application.gender,
            application.race_ethnicity,
            application.hometown,
            application.personal_activities,
            application.leader_supplement.co_leader,
        ] + [
            score.score for score in application.scores.all()
        ]


class TripLeadersCSV(GenericReportView):
    file_prefix = 'Leaders'

    def get_queryset(self):
        return Application.objects.leaders(
            self.get_trips_year()
        ).select_related(
            'assigned_trip__section',
            'assigned_trip__template'
        )

    header = ['name', 'netid', 'email', 'trip', 'section', 'gear requests']
    def get_row(self, leader):
        trip = leader.assigned_trip
        return [
            leader.name,
            leader.applicant.netid,
            leader.applicant.email,
            trip,
            trip.section.name if trip else '',
            leader.gear]


class CrooMembersCSV(TripLeadersCSV):
    file_prefix = 'Croo-Members'

    def get_queryset(self):
        return Application.objects.croo_members(self.get_trips_year())

    header = ['name', 'netid', 'croo']
    def get_row(self, croo_member):
        return [
            croo_member.name,
            croo_member.applicant.netid,
            croo_member.assigned_croo
        ]


class FinancialAidCSV(GenericReportView):

    file_prefix = 'Financial-aid'
    header = ['name', 'preferred name', 'netid', 'blitz', 'email']

    def get_queryset(self):
        return Registration.objects.want_financial_aid(
            self.get_trips_year()
        )

    def get_row(self, reg):
        user = reg.user
        return [user.name, reg.name, user.netid, user.email, reg.email]


class ExternalBusCSV(GenericReportView):

    file_prefix = 'External-Bus-Requests'
    header = [
        'name',
        'preferred name',
        'netid',
        'requested bus round trip',
        'requested bus to hanover',
        'requested bus from hanover'
    ]

    def get_queryset(self):
        return Registration.objects.want_bus(
            self.get_trips_year()
        ).select_related(
            'bus_stop_round_trip',
            'bus_stop_to_hanover',
            'bus_stop_from_hanover'
        )

    def get_row(self, reg):
        user = reg.user
        return [
            user.name,
            reg.name,
            user.netid,
            reg.bus_stop_round_trip or '',
            reg.bus_stop_to_hanover or '',
            reg.bus_stop_from_hanover or ''
        ]


class TrippeesCSV(GenericReportView):
    """
    All trippees going on trips
    """
    file_prefix = 'Trippees'

    def get_queryset(self):
        return IncomingStudent.objects.with_trip(self.get_trips_year())

    header = ['name', 'netid']
    def get_row(self, trippee):
        return [trippee.name, trippee.netid.upper()]


class Registrations(GenericReportView):
    """
    Information for all registered trippees.
    """
    file_prefix = 'Registrations'

    def get_queryset(self):
        return Registration.objects.filter(
            trips_year=self.get_trips_year()
        ).select_related(
            'user',
        ).prefetch_related(
            Prefetch('registrationsectionchoice_set',
                     queryset=RegistrationSectionChoice.objects.order_by('section')),
            Prefetch('registrationtriptypechoice_set',
                     queryset=RegistrationTripTypeChoice.objects.order_by('triptype'))
        )

    def get_header(self):
        header = [
            'name',
            'gender',
            'netid',
            'school',
            'exchange',
            'transfer',
            'international',
            'native',
            'fysep',
            'athlete?',
            'tshirt size',
            'height',
            'weight']
        header += [str(s) for s in self.sections]
        header += [str(t) for t in self.triptypes]
        header += [
            'schedule conflicts',
            'regular exercise?',
            'physical activities',
            'other activities',
            'swimming ability',
            'camping experience?',
            'hiking experience?',
            'hiking experience',
            'boating experience?',
            'boating experience',
            'other boating experience',
            'fishing experience',
            'horseback riding experience',
            'mountain biking experience',
            'sailing experience',
            'anything else?',
            'bus round trip',
            'bus to hanover',
            'bus from hanover',
        ]
        return header

    def get_row(self, r):
        row = [
            r.name,
            r.gender,
            r.user.netid,
            r.previous_school,
            yes_if_true(r.is_exchange),
            yes_if_true(r.is_transfer),
            yes_if_true(r.is_international),
            yes_if_true(r.is_native),
            yes_if_true(r.is_fysep),
            r.is_athlete,
            r.tshirt_size,
            r.height,
            r.weight,
        ]
        for pref, sxn in zip(r.registrationsectionchoice_set.all(), self.sections):
            assert pref.section_id == sxn.pk
            row += [pref.preference]

        for pref, tt in zip(r.registrationtriptypechoice_set.all(), self.triptypes):
            assert pref.triptype_id == tt.pk
            row += [pref.preference]

        row += [
            r.schedule_conflicts,
            yes_no(r.regular_exercise),
            r.physical_activities,
            r.other_activities,
            r.swimming_ability,
            yes_no(r.camping_experience),
            yes_no(r.hiking_experience),
            r.hiking_experience_description,
            yes_no(r.has_boating_experience),
            r.boating_experience,
            r.other_boating_experience,
            r.fishing_experience,
            r.horseback_riding_experience,
            r.mountain_biking_experience,
            r.sailing_experience,
            r.anything_else,
            r.bus_stop_round_trip,
            r.bus_stop_to_hanover,
            r.bus_stop_from_hanover,
        ]
        return row

    @cached_property
    def sections(self):
        return Section.objects.filter(trips_year=self.get_trips_year())

    @cached_property
    def triptypes(self):
        return TripType.objects.visible(self.get_trips_year())


class Charges(GenericReportView):
    """
    CSV file of charges to be applied to each trippee.

    All values are adjusted by financial aid, if applicable
    """
    file_prefix = 'Charges'

    def get_queryset(self):
        return IncomingStudent.objects.filter(
            (Q(trip_assignment__isnull=False) |
             Q(cancelled=True) |
             Q(registration__doc_membership=True) |
             Q(registration__green_fund_donation__gt=0)),
            trips_year=self.get_trips_year(),
        ).prefetch_related(
            'registration'
        )

    header = [
        'name',
        'netid',
        'total charge',
        'aid award (percentage)',
        'trip',
        'bus',
        'doc membership',
        'green fund',
        'cancellation'
    ]
    def get_row(self, incoming):
        reg = incoming.get_registration()
        return [
            incoming.name,
            incoming.netid,
            incoming.compute_cost(self.costs),
            incoming.financial_aid or '',
            incoming.trip_cost(self.costs) or '',
            incoming.bus_cost() or '',
            incoming.doc_membership_cost(self.costs) or '',
            incoming.green_fund_donation() or '',
            incoming.cancellation_cost(self.costs) or '',
        ]

    @property
    @cache_as('_costs')
    def costs(self):
        return Settings.objects.get(trips_year=self.get_trips_year())


class DocMembers(GenericReportView):
    """
    CSV file of registrations requesting DOC memberships.
    """
    file_prefix = 'DOC-Members'

    def get_queryset(self):
        return Registration.objects.filter(
            trips_year=self.get_trips_year(), doc_membership=True
        )

    header = ['name', 'netid', 'email']
    def get_row(self, reg):
        return [reg.user.name, reg.user.netid, reg.user.email]


def _tshirt_count(qs):
    """
    Return an OrderedDict with XS, S, M, L, XL, XXL keys, each
    with the number of shirts needed in that size.
    """
    counts = OrderedDict([(size, 0) for size in TSHIRT_SIZES])

    for size in TSHIRT_SIZES:
        counts[size] += qs.filter(tshirt_size=size).count()

    return counts


def leader_tshirts(trips_year):
    return _tshirt_count(Application.objects.filter(
        trips_year=trips_year, status=Application.LEADER
    ))


def croo_tshirts(trips_year):
    return _tshirt_count(Application.objects.filter(
        trips_year=trips_year, status=Application.CROO
    ))


def trippee_tshirts(trips_year):
    return _tshirt_count(Registration.objects.filter(
        trips_year=trips_year
    ))


class TShirts(DatabaseTemplateView):
    """
    Counts of all tshirt sizes requested by leaders, croos, and trippees.
    """
    template_name = "reports/tshirts.html"

    def extra_context(self):
        trips_year = self.get_trips_year()
        return {
            'leaders': leader_tshirts(trips_year),
            'croos': croo_tshirts(trips_year),
            'trippees': trippee_tshirts(trips_year)
        }


class Housing(GenericReportView):

    file_prefix = 'Housing'

    def get_queryset(self):
        return IncomingStudent.objects.filter(
            trips_year=self.get_trips_year()
        ).prefetch_related(
            'registration'
        )

    header = ['name', 'netid', 'trip', 'section', 'start date', 'end date',
              'native', 'fysep', 'international']
    def get_row(self, incoming):
        is_assigned = incoming.trip_assignment is not None
        reg = incoming.get_registration()
        trip = incoming.trip_assignment
        fmt = "%m/%d"
        return [
            incoming.name,
            incoming.netid,
            trip if is_assigned else "",
            trip.section.name if is_assigned else "",
            trip.section.trippees_arrive.strftime(fmt) if is_assigned else "",
            trip.section.return_to_campus.strftime(fmt) if is_assigned else "",
            'yes' if reg and reg.is_native else '',
            'yes' if reg and reg.is_fysep else '',
            'yes' if reg and reg.is_international else '',
        ]


class DietaryRestrictions(GenericReportView):

    file_prefix = 'Dietary-Restrictions'

    def get_queryset(self):
        return Registration.objects.filter(
            trips_year=self.get_trips_year()
        ).prefetch_related(
            'trippee__trip_assignment',
            'trippee__trip_assignment__section'
        )

    header = [
        'name', 'netid', 'section', 'trip',
        'food allergies',
        'dietary restrictions',
        'epipen'
    ]
    def get_row(self, reg):
        trip = reg.get_trip_assignment()
        return [
            reg.name,
            reg.user.netid,
            trip.section.name if trip else '',
            trip,
            reg.food_allergies,
            reg.dietary_restrictions,
            reg.get_epipen_display()
        ]


class MedicalInfo(GenericReportView):

    file_prefix = 'Medical-Info'

    def get_queryset(self):
        return Registration.objects.filter(
            trips_year=self.get_trips_year()
        )

    header = [
        'name', 'netid', 'section', 'trip',
        'medical conditions',
        'food allergies',
        'dietary restrictions',
        'epipen',
        'needs',
    ]
    def get_row(self, reg):
        trip = reg.get_trip_assignment()
        return [
            reg.name,
            reg.user.netid,
            trip.section.name if trip else '',
            trip,
            reg.medical_conditions,
            reg.food_allergies,
            reg.dietary_restrictions,
            reg.get_epipen_display(),
            reg.needs,
        ]

class VolunteerDietaryRestrictions(GenericReportView):

    file_prefix = 'Volunteer-Dietary-Restrictions'

    def get_queryset(self):
        return Application.objects.filter(
            trips_year=self.get_trips_year()
        ).filter(
            Q(status=Application.LEADER) | Q(status=Application.CROO)
        ).order_by(
            'status'
        )

    header = [
        'name',
        'netid',
        'role',
        'trip',
        'food allergies',
        'dietary restrictions',
        'epipen'
    ]
    def get_row(self, app):
        return [
            app.applicant.name,
            app.applicant.netid,
            app.status,
            app.assigned_trip or '',
            app.food_allergies,
            app.dietary_restrictions,
            app.get_epipen_display()
        ]


class Feelings(GenericReportView):

    file_prefix = 'Feelings'

    def get_queryset(self):
        return Registration.objects.filter(trips_year=self.get_trips_year())

    header = ['']
    def get_row(self, reg):
        return [reg.final_request]


class Foodboxes(GenericReportView):

    file_prefix = 'Foodboxes'

    def get_queryset(self):
        return Trip.objects.filter(trips_year=self.get_trips_year())

    header = [
        'trip',
        'section',
        'size',
        'full box',
        'half box',
        'supplement',
        'bagels'
    ]
    def get_row(self, trip):
        return [
            trip,
            trip.section.name,
            trip.size(),
            '1',
            '1' if trip.half_foodbox else '',
            '1' if trip.supp_foodbox else '',
            trip.bagels
        ]


class Statistics(DatabaseTemplateView):
    """
    Basic statistics regarding trippees
    """
    template_name = 'reports/statistics.html'

    def extra_context(self):
        IS = IncomingStudent

        counts = lambda qs: {
            'firstyear_count': qs.filter(incoming_status=IS.FIRSTYEAR).count(),
            'transfer_count': qs.filter(incoming_status=IS.TRANSFER).count(),
            'exchange_count': qs.filter(incoming_status=IS.EXCHANGE).count(),
            'unlabeled': qs.filter(incoming_status='').count(),
            'total': qs.count()
        }

        return {
            'with_trip': counts(IS.objects.with_trip(self.get_trips_year())),
            'cancelled': counts(IS.objects.cancelled(self.get_trips_year()))
        }
