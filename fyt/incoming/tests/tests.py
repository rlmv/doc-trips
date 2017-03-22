import os
from datetime import date, timedelta

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from model_mommy import mommy

from fyt.incoming.forms import RegistrationForm
from fyt.incoming.models import (
    AVAILABLE,
    FIRST_CHOICE,
    NOT_AVAILABLE,
    PREFER,
    IncomingStudent,
    Registration,
    RegistrationSectionChoice,
    RegistrationTripTypeChoice,
    Settings,
    sort_by_lastname,
)
from fyt.test import FytTestCase
from fyt.timetable.models import Timetable
from fyt.transport.models import Route, Stop
from fyt.trips.models import Section, Trip, TripType


def resolve_path(fname):
    """
    Resolve a filename in this directory.
    """
    return os.path.join(os.path.dirname(__file__), fname)


class IncomingStudentModelTestCase(FytTestCase):

    FILE = resolve_path('incoming_students.csv')

    def test_creating_Registration_automatically_links_to_existing_IncomingStudent(self):
        user = self.mock_incoming_student()
        trips_year = self.init_current_trips_year()
        # make existing info for user with netid
        incoming = mommy.make(IncomingStudent, netid=user.netid, trips_year=trips_year)
        reg = mommy.make(Registration, trips_year=trips_year, user=user)
        self.assertEqual(reg.trippee, incoming)

    def test_creating_Registration_without_incoming_info_does_nothing(self):
        user = self.mock_incoming_student()
        trips_year = self.init_current_trips_year()
        reg = mommy.make(Registration, trips_year=trips_year, user=user)
        with self.assertRaises(ObjectDoesNotExist):
            reg.trippee

    def test_creating_IncomingStudent_connects_to_existing_registration(self):
        user = self.mock_incoming_student()
        trips_year = self.init_current_trips_year()
        reg = mommy.make(Registration, trips_year=trips_year, user=user)
        incoming = mommy.make(IncomingStudent, netid=user.netid, trips_year=trips_year)
        # refresh registration
        reg = Registration.objects.get(pk=reg.pk)
        self.assertEqual(incoming.registration, reg)

    def test_get_hometown_parsing(self):
        trips_year = self.init_trips_year()
        with open(self.FILE) as f:
            IncomingStudent.objects.create_from_csv_file(f, trips_year.pk)
        incoming = IncomingStudent.objects.get(netid='id_2')
        self.assertEqual(incoming.get_hometown(), 'Chapel Hill, NC USA')

    def test_get_hometown_parsing_with_bad_formatting(self):
        trips_year = self.init_trips_year()
        incoming = mommy.make(
            IncomingStudent, trips_year=trips_year, address='what\nblah'
        )
        self.assertEqual(incoming.get_hometown(), 'what\nblah')

    def test_get_gender_without_registration(self):
        trips_year = self.init_trips_year()
        incoming = mommy.make(IncomingStudent, trips_year=trips_year, gender='MALE')
        self.assertEqual(incoming.get_gender(), 'male')

    def test_get_gender_with_registration(self):
        """ Pull from registration, if available """
        trips_year = self.init_trips_year()
        reg = mommy.make(Registration, trips_year=trips_year, gender='FEMALE')
        incoming = mommy.make(IncomingStudent, trips_year=trips_year,
                              gender='MALE', registration=reg)
        self.assertEqual(incoming.get_gender(), 'female')

    def test_financial_aid_in_range_0_to_100(self):
        trips_year = self.init_trips_year()

        with self.assertRaises(ValidationError):
            mommy.prepare(
                IncomingStudent, trips_year=trips_year,
                financial_aid=-1
            ).full_clean()

        with self.assertRaises(ValidationError):
            mommy.prepare(
                IncomingStudent, trips_year=trips_year,
                financial_aid=101
            ).full_clean()

        mommy.prepare(
            IncomingStudent, trips_year=trips_year,
            financial_aid=100
        ).full_clean()

    def test_compute_base_cost(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year, trips_cost=100)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=mommy.make(Trip),
            financial_aid=0, bus_assignment_round_trip=None
        )
        self.assertEqual(inc.compute_cost(), 100)

    def test_compute_cost_with_financial_aid(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year, trips_cost=100)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=mommy.make(Trip),
            financial_aid=35, bus_assignment_round_trip=None
        )
        self.assertEqual(inc.compute_cost(), 65)

    def test_compute_cost_with_bus(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year, trips_cost=100)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=mommy.make(Trip),
            financial_aid=25, bus_assignment_round_trip__cost_round_trip=25
        )
        self.assertEqual(inc.compute_cost(), 93.75)

    def test_compute_cost_with_doc_membership(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year, trips_cost=100, doc_membership_cost=50)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=mommy.make(Trip),
            financial_aid=25, bus_assignment_round_trip__cost_round_trip=25,
            registration__doc_membership=True
        )
        self.assertEqual(inc.compute_cost(), 131.25)

    def test_compute_cost_with_green_fund_contribution(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year, trips_cost=100, doc_membership_cost=50)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=mommy.make(Trip),
            financial_aid=25, bus_assignment_round_trip__cost_round_trip=25,
            registration__doc_membership=True,
            registration__green_fund_donation=290
        )
        self.assertEqual(inc.compute_cost(), 421.25)

    def test_compute_cost_with_no_trip_assignment_but_with_doc_membership(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year, trips_cost=100, doc_membership_cost=50)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=None,
            financial_aid=0, bus_assignment_round_trip=None,
            registration__doc_membership=True
        )
        self.assertEqual(inc.compute_cost(), 50)

    def test_compute_cost_with_cancelled_trip(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year, trips_cost=100)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=None,
            cancelled=True
        )
        # still charged if cancels last-minute
        self.assertEqual(inc.compute_cost(), 100)

    def test_compute_cost_with_cancelled_trip_and_custom_cancellation_fee(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year, trips_cost=100)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=None,
            cancelled=True,
            cancelled_fee=13
        )
        self.assertEqual(inc.compute_cost(), 13)

    def test_compute_cost_with_passed_costs(self):
        trips_year = self.init_trips_year()
        costs = mommy.make(Settings, trips_year=trips_year, trips_cost=100)
        inc = mommy.make(IncomingStudent, trips_year=trips_year)
        with self.assertNumQueries(0):
            inc.compute_cost(costs)
        self.assertEqual(inc.compute_cost(), inc.compute_cost(costs))

    def test_cancellation_cost(self):
        trips_year = self.init_trips_year()
        costs = mommy.make(Settings, trips_year=trips_year, trips_cost=100)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=None,
            cancelled=True,
            financial_aid=70
        )
        self.assertEqual(inc.cancellation_cost(costs), 30)

    def test_cancellation_cost_with_fee_override(self):
        trips_year = self.init_trips_year()
        costs = mommy.make(Settings, trips_year=trips_year, trips_cost=100)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=None,
            cancelled=True,
            cancelled_fee=13
        )
        self.assertEqual(inc.cancellation_cost(costs), 13)

    def test_trip_cost_with_no_trip(self):
        trips_year = self.init_trips_year()
        costs = mommy.make(Settings, trips_year=trips_year, trips_cost=100)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=None,
        )
        self.assertEqual(inc.trip_cost(costs), 0)

    def test_doc_membership_cost(self):
        trips_year = self.init_trips_year()
        costs = mommy.make(Settings, trips_year=trips_year, doc_membership_cost=100)
        inc = mommy.make(
            IncomingStudent, trips_year=trips_year,
            trip_assignment=None,
            registration__doc_membership=True,
            financial_aid=60
        )
        self.assertEqual(inc.doc_membership_cost(costs), 40)

    def test_netid_and_trips_year_are_unique(self):
        trips_year = self.init_trips_year()
        mommy.make(IncomingStudent, trips_year=trips_year, netid='w')
        with self.assertRaises(IntegrityError):
            mommy.make(IncomingStudent, trips_year=trips_year, netid='w')

    def test_bus_assignment_is_either_one_way_or_round_trip(self):
        msg = "Cannot have round-trip AND one-way bus assignments"
        with self.assertRaisesRegexp(ValidationError, msg):
            mommy.prepare(
                IncomingStudent,
                bus_assignment_round_trip=mommy.make(Stop),
                bus_assignment_to_hanover=mommy.make(Stop)
            ).full_clean()
        with self.assertRaisesRegexp(ValidationError, msg):
            mommy.prepare(
                IncomingStudent,
                bus_assignment_round_trip=mommy.make(Stop),
                bus_assignment_from_hanover=mommy.make(Stop)
            ).full_clean()

    def test_bus_cost_with_round_trip(self):
        inc = mommy.make(
            IncomingStudent,
            bus_assignment_round_trip=mommy.make(Stop, cost_round_trip=100, cost_one_way=15),
            financial_aid=35
        )
        self.assertEqual(inc.bus_cost(), 65)

    def test_bus_cost_with_one_way(self):
        inc = mommy.make(
            IncomingStudent,
            bus_assignment_to_hanover=mommy.make(
                Stop, cost_round_trip=3, cost_one_way=30),
            bus_assignment_from_hanover=mommy.make(
                Stop, cost_round_trip=1, cost_one_way=70),
            financial_aid=10
        )
        self.assertEqual(inc.bus_cost(), 90)

    def test_bus_cost_is_zero_if_no_bus(self):
        inc = mommy.make(
            IncomingStudent,
            bus_assignment_round_trip=None,
            bus_assignment_to_hanover=None,
            bus_assignment_from_hanover=None,
        )
        self.assertEqual(inc.bus_cost(), 0)

    def test_get_bus_stop_to_and_from_hanover_with_round_trip(self):
        stop = mommy.make(Stop)
        inc = mommy.make(
            IncomingStudent,
            bus_assignment_round_trip=stop
        )
        self.assertEqual(inc.get_bus_to_hanover(), stop)
        self.assertEqual(inc.get_bus_from_hanover(), stop)

    def test_get_bus_stop_to_hanover_one_way(self):
        stop = mommy.make(Stop)
        inc = mommy.make(
            IncomingStudent,
            bus_assignment_to_hanover=stop
        )
        self.assertEqual(inc.get_bus_to_hanover(), stop)

    def test_get_bus_stop_from_hanover_one_way(self):
        stop = mommy.make(Stop)
        inc = mommy.make(
            IncomingStudent,
            bus_assignment_from_hanover=stop
        )
        self.assertEqual(inc.get_bus_from_hanover(), stop)

    def test_lastname(self):
        inc = mommy.make(IncomingStudent, name='Rachek Zhao')
        self.assertEqual(inc.lastname, 'Zhao')

    def test_sort_by_lastname(self):
        inc1 = mommy.make(IncomingStudent, name='Rachel Zhao')
        inc2 = mommy.make(IncomingStudent, name='Lara P. Balick')
        inc3 = mommy.make(IncomingStudent, name='William A. P. Wolfe-McGuire')
        self.assertEqual([inc2, inc3, inc1], sort_by_lastname([inc1, inc2, inc3]))


class RegistrationModelTestCase(FytTestCase):

    def test_must_agree_to_waiver(self):
        with self.assertRaisesMessage(
                ValidationError, "You must agree to the waiver"):
            mommy.make(Registration, waiver=False).full_clean()

    def test_get_trip_assignment_returns_assignment(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(Trip, trips_year=trips_year)
        reg = mommy.make(Registration, trips_year=trips_year)
        trippee = mommy.make(IncomingStudent, trips_year=trips_year, trip_assignment=trip, registration=reg)
        self.assertEqual(trip, reg.get_trip_assignment())

    def test_get_trip_assignment_with_no_assigned_trip_returns_None(self):
        trips_year = self.init_current_trips_year()
        reg = mommy.make(Registration, trips_year=trips_year)
        trippee = mommy.make(IncomingStudent, trips_year=trips_year, trip_assignment=None, registration=reg)
        self.assertIsNone(reg.get_trip_assignment())

    def test_get_trip_assignment_with_no_IncomingStudent_returns_None(self):
        trips_year = self.init_current_trips_year()
        reg = mommy.make(Registration, trips_year=trips_year)
        self.assertIsNone(reg.get_trip_assignment())

    def test_nonswimmer_property(self):
        trips_year = self.init_current_trips_year()
        non_swimmer =  mommy.make(Registration, trips_year=trips_year, swimming_ability=Registration.NON_SWIMMER)
        self.assertTrue(non_swimmer.is_non_swimmer)
        for choice in [Registration.BEGINNER, Registration.COMPETENT, Registration.EXPERT]:
            swimmer = mommy.make(Registration, trips_year=trips_year, swimming_ability=choice)
            self.assertFalse(swimmer.is_non_swimmer)

    def test_base_trip_choice_queryset_filters_for_nonswimmers(self):
        trips_year = self.init_current_trips_year()
        trip1 = mommy.make(Trip, trips_year=trips_year, template__swimtest_required=True)
        trip2 = mommy.make(Trip, trips_year=trips_year, template__swimtest_required=False)

        reg = mommy.make(Registration, trips_year=trips_year, swimming_ability=Registration.NON_SWIMMER)
        reg.set_section_preference(trip1.section, PREFER)
        reg.set_section_preference(trip2.section, PREFER)

        self.assertEqual(list(reg._base_trips_qs()), [trip2])

    def test_base_trips_qs_filters_for_preferred_and_available_sections(self):
        trips_year = self.init_current_trips_year()
        trip1 = mommy.make(Trip, trips_year=trips_year)
        trip2 = mommy.make(Trip, trips_year=trips_year)
        trip3 = mommy.make(Trip, trips_year=trips_year)

        reg = mommy.make(Registration, trips_year=trips_year, swimming_ability=Registration.COMPETENT)
        reg.set_section_preference(trip1.section, PREFER)
        reg.set_section_preference(trip2.section, AVAILABLE)

        self.assertEqual(set(reg._base_trips_qs()), set([trip1, trip2]))

    def test_get_firstchoice_trips(self):
        trips_year = self.init_current_trips_year()
        section1 = mommy.make('Section', trips_year=trips_year)
        section2 = mommy.make('Section', trips_year=trips_year)
        firstchoice_triptype = mommy.make('TripType', trips_year=trips_year)
        trip1 = mommy.make(Trip, trips_year=trips_year, section=section1, template__triptype=firstchoice_triptype)
        trip2 = mommy.make(Trip, trips_year=trips_year, section=section2, template__triptype=firstchoice_triptype)

        reg = mommy.make(Registration, trips_year=trips_year,
                         swimming_ability=Registration.COMPETENT)
        reg.set_section_preference(section1, AVAILABLE)
        reg.set_triptype_preference(firstchoice_triptype, FIRST_CHOICE)

        self.assertEqual([trip1], list(reg.get_firstchoice_trips()))

    def test_get_preferred_trips(self):

        trips_year = self.init_current_trips_year()
        section1 = mommy.make('Section', trips_year=trips_year)
        section2 = mommy.make('Section', trips_year=trips_year)
        triptype = mommy.make('TripType', trips_year=trips_year)
        trip1 = mommy.make(Trip, trips_year=trips_year, section=section1, template__triptype=triptype)
        trip2 = mommy.make(Trip, trips_year=trips_year, section=section2, template__triptype=triptype)
        trip3 = mommy.make(Trip, trips_year=trips_year, section=section1)

        reg = mommy.make(Registration, trips_year=trips_year,
                         swimming_ability=Registration.COMPETENT)
        reg.set_section_preference(section1, PREFER)
        reg.set_triptype_preference(triptype, PREFER)

        self.assertEqual([trip1], list(reg.get_preferred_trips()))

    def test_get_available_trips(self):

        trips_year = self.init_current_trips_year()
        section1 = mommy.make('Section', trips_year=trips_year)
        section2 = mommy.make('Section', trips_year=trips_year)
        triptype = mommy.make('TripType', trips_year=trips_year)
        trip1 = mommy.make(Trip, trips_year=trips_year, section=section1, template__triptype=triptype)
        trip2 = mommy.make(Trip, trips_year=trips_year, section=section2, template__triptype=triptype)
        trip3 = mommy.make(Trip, trips_year=trips_year, section=section1)

        reg = mommy.make(Registration, trips_year=trips_year,
                         swimming_ability=Registration.COMPETENT)
        reg.set_section_preference(section1, PREFER)
        reg.set_triptype_preference(triptype, AVAILABLE)

        self.assertEqual([trip1], list(reg.get_available_trips()))

    def test_get_incoming_student(self):
        trips_year = self.init_current_trips_year()
        reg = mommy.make(Registration, trips_year=trips_year)
        self.assertIsNone(reg.get_incoming_student())
        incoming = mommy.make(IncomingStudent, trips_year=trips_year,
                              registration=reg)
        reg = Registration.objects.get(pk=reg.pk)
        self.assertEqual(reg.get_incoming_student(), incoming)

    def test_match(self):
        user = self.mock_incoming_student()
        trips_year = self.init_current_trips_year()
        incoming = mommy.make(IncomingStudent, netid=user.netid, trips_year=trips_year)
        reg = mommy.make(Registration, trips_year=trips_year, user=user)
        # clear automatic connections
        incoming.registration = None
        incoming.save()
        reg = Registration.objects.get(pk=reg.pk)
        reg.match()
        self.assertEqual(reg.trippee, incoming)

    def test_cannot_request_round_trip_and_one_way_bus(self):
        with self.assertRaisesRegex(ValidationError, "round-trip AND a one-way"):
            mommy.make(
                Registration,
                bus_stop_round_trip=mommy.make(Stop),
                bus_stop_to_hanover=mommy.make(Stop),
                waiver=True
            ).full_clean()
        with self.assertRaisesRegex(ValidationError, "round-trip AND a one-way"):
            mommy.make(
                Registration,
                bus_stop_round_trip=mommy.make(Stop),
                bus_stop_from_hanover=mommy.make(Stop),
                waiver=True
            ).full_clean()


class ImportIncomingStudentsTestCase(FytTestCase):

    FILE = resolve_path('incoming_students.csv')
    FILE_WITH_BLANKS = resolve_path('incoming_students_with_blank_id.csv')

    def test_create_from_csv(self):
        trips_year = self.init_current_trips_year().pk
        with open(self.FILE) as f:
            (created, existing) = IncomingStudent.objects.create_from_csv_file(f, trips_year)
        self.assertEqual(set(['id_1', 'id_2']), set(created))
        self.assertEqual(existing, [])
        # are student objects created?
        IncomingStudent.objects.get(netid='id_1')
        IncomingStudent.objects.get(netid='id_2')

    def test_ignore_existing_students(self):
        trips_year = self.init_current_trips_year().pk
        with open(self.FILE) as f:
            (created, existing) = IncomingStudent.objects.create_from_csv_file(f, trips_year)
        with open(self.FILE) as f:
            (created, existing) = IncomingStudent.objects.create_from_csv_file(f, trips_year)
        self.assertEqual(set(['id_1', 'id_2']), set(existing))
        self.assertEqual(created, [])

    def test_ignore_rows_without_id(self):
        trips_year = self.init_current_trips_year().pk

        with open(self.FILE_WITH_BLANKS) as f:
            (created, existing) = IncomingStudent.objects.create_from_csv_file(f, trips_year)

        self.assertEqual(set(['id_1']), set(created))
        self.assertEqual(existing, [])
        # are student objects created?
        IncomingStudent.objects.get(netid='id_1')


class ImportIncomingStudentHinmanBoxes(FytTestCase):

    FILE = resolve_path('hinman_boxes.csv')

    def test_import_from_csv(self):
        trips_year = self.init_trips_year()
        incoming = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            netid='d34898x',
            hinman_box=''
        )
        with open(self.FILE) as f:
            imported = IncomingStudent.objects.update_hinman_boxes(f, trips_year)

        incoming.refresh_from_db()
        self.assertEqual(incoming.hinman_box, '2884')
        self.assertEqual(imported, [incoming])


class IncomingStudentsManagerTestCase(FytTestCase):

    def test_unregistered(self):
        trips_year = self.init_current_trips_year()
        registration = mommy.make(Registration, trips_year=trips_year)
        registered = mommy.make(IncomingStudent, trips_year=trips_year, registration=registration)
        unregistered = mommy.make(IncomingStudent, trips_year=trips_year)
        self.assertQsEqual(IncomingStudent.objects.unregistered(trips_year), [unregistered])

    def test_availability_for_trip(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(Trip, trips_year=trips_year)

        # Available for both the section and triptype
        available = mommy.make(IncomingStudent, trips_year=trips_year,
                               registration=mommy.make(Registration, trips_year=trips_year))
        available.registration.set_section_preference(trip.section, PREFER)
        available.registration.set_triptype_preference(trip.template.triptype, AVAILABLE)

        # Available for the section but not the triptype
        unavailable1 = mommy.make(IncomingStudent, trips_year=trips_year,
                                  registration=mommy.make(Registration, trips_year=trips_year))
        unavailable1.registration.set_section_preference(trip.section, PREFER)

        # Available for the triptype, but not the section
        unavailable2 = mommy.make(IncomingStudent, trips_year=trips_year,
                                 registration=mommy.make(Registration, trips_year=trips_year))
        unavailable2.registration.set_section_preference(trip.section, NOT_AVAILABLE)
        unavailable2.registration.set_section_preference(mommy.make(Section, trips_year=trips_year), PREFER)
        unavailable2.registration.set_triptype_preference(trip.template.triptype, AVAILABLE)

        self.assertQsEqual(IncomingStudent.objects.available_for_trip(trip), [available])

    def test_non_swimmer_availability_for_trip(self):
        trips_year = self.init_current_trips_year()
        trip = mommy.make(
            Trip, trips_year=trips_year,
            template__swimtest_required=True
        )
        available = mommy.make(
            IncomingStudent, trips_year=trips_year,
            registration__swimming_ability=Registration.BEGINNER
        )
        available.registration.set_section_preference(trip.section, PREFER)
        available.registration.set_triptype_preference(trip.template.triptype, AVAILABLE)

        unavailable = mommy.make(
            IncomingStudent, trips_year=trips_year,
            registration__swimming_ability=Registration.NON_SWIMMER
        )
        unavailable.registration.set_section_preference(trip.section, PREFER)
        unavailable.registration.set_triptype_preference(trip.template.triptype, AVAILABLE)

        self.assertQsEqual(IncomingStudent.objects.available_for_trip(trip), [available])

    def test_passengers_to_hanover(self):
        trips_year = self.init_trips_year()
        rte = mommy.make(Route, trips_year=trips_year, category=Route.EXTERNAL)
        sxn = mommy.make(Section, trips_year=trips_year)
        psngr1 = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment_round_trip__route=rte,
            trip_assignment__section=sxn
        )
        psngr2 = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment_to_hanover__route=rte,
            trip_assignment__section=sxn
        )
        not_psngr = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment_from_hanover__route=rte,
            trips_assignment__section=sxn
        )
        target = [psngr1, psngr2]
        actual = IncomingStudent.objects.passengers_to_hanover(
            trips_year, rte, sxn
        )
        self.assertQsEqual(actual, target)

    def test_passengers_from_hanover(self):
        trips_year = self.init_trips_year()
        rte = mommy.make(Route, trips_year=trips_year, category=Route.EXTERNAL)
        sxn = mommy.make(Section, trips_year=trips_year)
        psngr1 = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment_round_trip__route=rte,
            trip_assignment__section=sxn
        )
        psngr2 = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment_from_hanover__route=rte,
            trip_assignment__section=sxn
        )
        not_psngr = mommy.make(
            IncomingStudent, trips_year=trips_year,
            bus_assignment_to_hanover__route=rte,
            trips_assignment__section=sxn
        )
        target = [psngr1, psngr2]
        actual = IncomingStudent.objects.passengers_from_hanover(
            trips_year, rte, sxn
        )
        self.assertQsEqual(actual, target)

    def test_with_trip(self):
        trips_year = self.init_trips_year()
        trip = mommy.make(
            Trip,
            trips_year=trips_year
        )
        assigned = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=trip
        )
        not_assigned = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=None
        )
        actual = list(IncomingStudent.objects.with_trip(trips_year))
        self.assertEqual(actual, [assigned])

    def test_cancelled(self):
        trips_year = self.init_trips_year()
        cancelled = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            cancelled=True
        )
        not_cancelled = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            cancelled=False,
            trip_assignment=mommy.make(Trip)
        )
        self.assertQsEqual(IncomingStudent.objects.cancelled(trips_year), [cancelled])


class RegistrationViewsTestCase(FytTestCase):

    csrf_checks = False

    def test_registration_with_anonymous_user(self):
        self.init_current_trips_year()
        self.app.get(reverse('incoming:register'))

    def test_registration_connects_to_incoming(self):
        trips_year = self.init_current_trips_year()
        t = Timetable.objects.timetable()
        t.trippee_registrations_open += timedelta(-1)
        t.trippee_registrations_close += timedelta(1)
        t.save()
        mommy.make(Settings, trips_year=trips_year)
        user = self.mock_incoming_student()
        student = mommy.make(IncomingStudent, trips_year=trips_year, netid=user.netid)
        reg_data = {
            'name': 'test',
            'gender': 'hi',
            'previous_school': 'nah',
            'phone': '134',
            'email': 'asf@gmail.com',
            'tshirt_size': 'L',
            'regular_exercise': False,
            'swimming_ability': 'BEGINNER',
            'camping_experience': False,
            'hiking_experience': True,
            'financial_assistance': True,
            'waiver': True,
            'doc_membership': False,
            'green_fund_donation': 0,
        }
        url = reverse('incoming:register')
        self.app.post(url, reg_data, user=user)
        registration = Registration.objects.get()
        student = IncomingStudent.objects.get()
        self.assertEqual(registration.trippee, student)

    def test_non_student_registration(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year)
        url = reverse('db:registration:nonstudent', kwargs={'trips_year': trips_year})
        data = {
            'name': 'name',
            'gender': 'm',
            'previous_school': 'nah',
            'phone': '134',
            'email': 'asf@gmail.com',
            'tshirt_size': 'L',
            'regular_exercise': False,
            'swimming_ability': 'BEGINNER',
            'camping_experience': False,
            'hiking_experience': True,
            'financial_assistance': True,
            'waiver': True,
            'doc_membership': False,
            'green_fund_donation': 0,
        }
        resp = self.app.post(url, data, user=self.mock_director()).follow()

        registration = Registration.objects.get()
        user = registration.user
        trippee = registration.trippee

        self.assertEqual(user.name, 'name')
        self.assertEqual(user.netid, 'name')
        self.assertEqual(user.email, 'asf@gmail.com')

        self.assertEqual(resp.request.path, trippee.detail_url())
        self.assertEqual(trippee.name, 'name')
        self.assertEqual(trippee.netid, 'name')
        self.assertEqual(trippee.email, 'asf@gmail.com')
        self.assertEqual(trippee.blitz, 'asf@gmail.com')
        self.assertEqual(trippee.phone, '134')
        self.assertEqual(trippee.gender, 'm')


class RegistrationFormTestCase(FytTestCase):

    def setUp(self):
        self.trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=self.trips_year)  # must exist
        self.reg = mommy.make(Registration, trips_year=self.trips_year)

    def test_registration_form_without_instance_uses_current_trips_year(self):
        form = RegistrationForm()
        self.assertEqual(form.trips_year, self.trips_year)

    def test_registration_form_uses_trips_year_from_instance(self):
        prev_trips_year = self.init_previous_trips_year()
        mommy.make(Settings, trips_year=prev_trips_year)  # must exist
        reg = mommy.make(Registration, trips_year=prev_trips_year)
        form = RegistrationForm(instance=reg)
        self.assertEqual(form.trips_year, prev_trips_year)

    def test_section_and_triptype_preferences(self):
        triptype = mommy.make(TripType, pk=1, trips_year=self.trips_year)
        section = mommy.make(Section, pk=1, trips_year=self.trips_year,
                             leaders_arrive=date(2015, 1, 1), name='A')

        form = RegistrationForm(instance=self.reg, data={
            'name': 'test',
            'gender': 'hi',
            'previous_school': 'nah',
            'phone': '134',
            'email': 'asf@gmail.com',
            'tshirt_size': 'L',
            'regular_exercise': False,
            'swimming_ability': 'BEGINNER',
            'camping_experience': False,
            'hiking_experience': True,
            'financial_assistance': True,
            'waiver': True,
            'doc_membership': False,
            'green_fund_donation': 0,
            'triptype_1': 'FIRST CHOICE',
            'section_1': 'PREFER'
        })
        form.save()

        self.assertEqual(form.fields['section_1'].label,
                         'A &mdash; Jan 02 to Jan 06')

        tts = self.reg.registrationtriptypechoice_set.all()
        self.assertEqual(len(tts), 1)
        self.assertEqual(tts[0].triptype, triptype)
        self.assertEqual(tts[0].preference, 'FIRST CHOICE')

        secs = self.reg.registrationsectionchoice_set.all()
        self.assertEqual(len(secs), 1)
        self.assertEqual(secs[0].section, section)
        self.assertEqual(secs[0].preference, 'PREFER')



class IncomingStudentViewsTestCase(FytTestCase):

    def test_delete_view(self):
        trips_year = self.init_current_trips_year()
        incoming = mommy.make(IncomingStudent, trips_year=trips_year)
        url = incoming.delete_url()
        res = self.app.get(url, user=self.mock_director())
        res = res.form.submit().follow()
        self.assertEqual(res.request.path,
                         reverse('db:incomingstudent:index', kwargs={'trips_year': trips_year}))
        with self.assertRaises(IncomingStudent.DoesNotExist):
            IncomingStudent.objects.get(pk=incoming.pk)


class RegistrationManagerTestCase(FytTestCase):

    def test_requesting_financial_aid(self):
        trips_year = self.init_current_trips_year()
        requesting = mommy.make(
            Registration, trips_year=trips_year,
            financial_assistance=True
        )
        not_requesting = mommy.make(
            Registration, trips_year=trips_year,
            financial_assistance=False
        )
        self.assertEqual(
            [requesting], list(Registration.objects.want_financial_aid(trips_year))
        )

    def test_requesting_bus(self):
        trips_year = self.init_current_trips_year()
        stop = mommy.make(
            Stop, trips_year=trips_year, route__category=Route.EXTERNAL
        )
        r1 = mommy.make(
            Registration, trips_year=trips_year, bus_stop_round_trip=stop
        )
        r2 = mommy.make(
            Registration, trips_year=trips_year, bus_stop_to_hanover=stop
        )
        r3 = mommy.make(
            Registration, trips_year=trips_year, bus_stop_from_hanover=stop
        )
        not_requesting = mommy.make(Registration, trips_year=trips_year)
        self.assertQsEqual(Registration.objects.want_bus(trips_year), [r1, r2, r3])

    def test_unmatched(self):
        trips_year = self.init_current_trips_year()
        matched = mommy.make(Registration, trips_year=trips_year)
        mommy.make(IncomingStudent, trips_year=trips_year, registration=matched)
        unmatched = mommy.make(Registration, trips_year=trips_year)
        self.assertEqual([unmatched], list(Registration.objects.unmatched(trips_year)))
