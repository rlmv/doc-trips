import csv
import tempfile
from contextlib import contextmanager
from datetime import date

from django.urls import reverse
from model_mommy import mommy

from fyt.applications.models import Grader, Question, Volunteer
from fyt.applications.tests import ApplicationTestMixin
from fyt.croos.models import Croo
from fyt.gear.models import Gear, GearRequest
from fyt.incoming.models import IncomingStudent, Registration, Settings
from fyt.reports.views import croo_tshirts, leader_tshirts, trippee_tshirts
from fyt.test import FytTestCase
from fyt.transport.models import ExternalBus, Route
from fyt.trips.models import Section, Trip, TripType
from fyt.utils.choices import L, M, S, XL, XS, XXL


@contextmanager
def save_and_open_csv(resp):
    """
    Save the file content return by response and
    open a CSV reader object over the saved file.
    """
    f = tempfile.NamedTemporaryFile()
    f.write(resp.content)
    with open(f.name) as f: # open in non-binary mode
        yield csv.DictReader(f)


class ReportViewsTestCase(FytTestCase, ApplicationTestMixin):

    maxDiff = None

    def assertStopsIteration(self, iter):
        with self.assertRaises(StopIteration):
            next(iter)

    def assertCsvReturns(self, urlpattern, target, url_kwargs=None, num_queries=None):
        """
        Test a view by visiting it with director priveleges and
        comparing returned csv to ``target``.

        ``urlpattern`` is a reversable pattern,
        ``target`` is a list of ``dicts``
        """
        kwargs = {'trips_year': self.trips_year}

        if url_kwargs is not None:
            kwargs.update(url_kwargs)

        url = reverse(urlpattern, kwargs=kwargs)
        director = self.make_director()

        if num_queries:
            with self.assertNumQueries(num_queries):
                resp = self.app.get(url, user=director)
        else:
            resp = self.app.get(url, user=director)

        self.assertTrue(
            resp['Content-Disposition'].startswith('attachment; filename="')
        )

        with save_and_open_csv(resp) as csvf:
            self.assertEqual([dict(r) for r in csvf], target)

    def setUp(self):
        self.init_trips_year()

    def test_volunteer_csv(self):
        self.make_score_values()
        question = mommy.make(Question, trips_year=self.trips_year)
        app = self.make_application(trips_year=self.trips_year)
        app.croo_willing = False
        app.save()
        app.answer_question(question, 'An answer')
        mommy.make(Grader).add_score(app, self.V4, self.V2)
        mommy.make(Grader).add_score(app, self.V5, self.V1)
        mommy.make(Grader).add_score(app, self.V4, self.V3)

        self.assertCsvReturns(
            'core:reports:all_apps',
            [
                {
                    'name': app.name,
                    'netid': app.applicant.netid,
                    'status': app.status,
                    'leader app': 'yes',
                    'croo app': 'no',
                    'class year': str(app.class_year),
                    'gender': app.gender,
                    'race/ethnicity': app.race_ethnicity,
                    'hometown': app.hometown,
                    'clubs/interests': app.personal_activities,
                    'co-leader': app.leader_supplement.co_leader,
                    'avg leader score': '4.3',
                    'leader score 1': '4.0',
                    'leader score 2': '5.0',
                    'leader score 3': '4.0',
                    'avg croo score': '2.0',
                    'croo score 1': '2.0',
                    'croo score 2': '1.0',
                    'croo score 3': '3.0',
                }
            ],
            num_queries=19,
        )

    def test_trip_leader_csv(self):
        trip = mommy.make(Trip, trips_year=self.trips_year)
        leader = self.make_application(
            trips_year=self.trips_year,
            status=Volunteer.LEADER,
            trip_assignment=trip,
            applicant__name='Alice',
            gear='pogo stick',
        )

        leader_without_trip = self.make_application(
            trips_year=self.trips_year,
            status=Volunteer.LEADER,
            trip_assignment=None,
            applicant__name='Bob',
        )

        not_leader = self.make_application(trips_year=self.trips_year)

        self.assertCsvReturns(
            'core:reports:leaders',
            [
                {
                    'name': 'Alice',
                    'netid': leader.applicant.netid,
                    'email': leader.applicant.email,
                    'trip': str(trip),
                    'section': trip.section.name,
                    'gear requests': 'pogo stick',
                },
                {
                    'name': 'Bob',
                    'netid': leader_without_trip.applicant.netid,
                    'email': leader_without_trip.applicant.email,
                    'trip': '',
                    'section': '',
                    'gear requests': '',
                },
            ],
        )

    def test_croo_members_csv(self):
        croo = mommy.make(Croo, trips_year=self.trips_year)
        crooling = self.make_application(
            trips_year=self.trips_year, status=Volunteer.CROO, croo_assignment=croo
        )
        not_croo = self.make_application(trips_year=self.trips_year)

        self.assertCsvReturns(
            'core:reports:croo_members',
            [
                {
                    'name': crooling.name,
                    'netid': crooling.applicant.netid,
                    'croo': str(crooling.croo_assignment),
                }
            ],
        )

    def test_trippees_csv(self):
        trippee = mommy.make(
            IncomingStudent,
            trips_year=self.trips_year,
            trip_assignment=mommy.make(Trip),
        )
        not_trippee = mommy.make(
            IncomingStudent, trips_year=self.trips_year, trip_assignment=None
        )
        self.assertCsvReturns(
            'core:reports:trippees',
            [{'name': trippee.name, 'netid': trippee.netid.upper()}],
        )

    def test_registrations_csv(self):
        r = mommy.make(
            Registration, trips_year=self.trips_year, name='Bob', gender='male'
        )
        section = mommy.make(Section, trips_year=self.trips_year, name='A')
        r.set_section_preference(section, 'PREFER')
        triptype = mommy.make(TripType, trips_year=self.trips_year, name='Hiking 3')
        r.set_triptype_preference(triptype, 'AVAILABLE')

        self.assertCsvReturns(
            'core:reports:registrations',
            [
                {
                    'name': 'Bob',
                    'gender': 'male',
                    'netid': r.user.netid,
                    'school': r.previous_school,
                    'exchange': '',
                    'transfer': '',
                    'international': '',
                    'native': '',
                    'fysep': '',
                    'athlete?': '',
                    'tshirt size': r.tshirt_size,
                    'height': r.height,
                    'weight': r.weight,
                    'Section A': 'PREFER',
                    'Hiking 3': 'AVAILABLE',
                    'schedule conflicts': '',
                    'regular exercise?': 'no',
                    'physical activities': r.physical_activities,
                    'other activities': r.other_activities,
                    'swimming ability': r.swimming_ability,
                    'camping experience?': 'no',
                    'hiking experience?': 'no',
                    'hiking experience': r.hiking_experience_description,
                    'boating experience?': 'no',
                    'boating experience': '',
                    'other boating experience': '',
                    'fishing experience': '',
                    'horseback riding experience': '',
                    'mountain biking experience': '',
                    'sailing experience': '',
                    'anything else?': '',
                    'bus round trip': '',
                    'bus to hanover': '',
                    'bus from hanover': '',
                }
            ],
        )

    def test_charges_report(self):
        mommy.make(
            Settings, trips_year=self.trips_year, doc_membership_cost=91, trips_cost=250
        )

        # incoming student to be charged:
        incoming1 = mommy.make(
            IncomingStudent,
            name='1',
            trips_year=self.trips_year,
            trip_assignment__trips_year=self.trips_year,  # force trip to exist
            bus_assignment_round_trip__cost_round_trip=100,
            financial_aid=10,
            registration__doc_membership=True,
            registration__green_fund_donation=20,
        )

        # another, without a registration
        incoming2 = mommy.make(
            IncomingStudent,
            name='2',
            trips_year=self.trips_year,
            trip_assignment__trips_year=self.trips_year,  # ditto
            financial_aid=0,
        )

        # another with no trip but with doc membership
        incoming3 = mommy.make(
            IncomingStudent,
            name='3',
            trips_year=self.trips_year,
            trip_assignment=None,
            financial_aid=0,
            registration__doc_membership=True,
        )

        # another with no trip, no membership, but green fund donation
        incoming4 = mommy.make(
            IncomingStudent,
            name='4',
            trips_year=self.trips_year,
            trip_assignment=None,
            financial_aid=0,
            registration__doc_membership=False,
            registration__green_fund_donation=12,
        )

        # last-minute cancellation
        incoming5 = mommy.make(
            IncomingStudent,
            name='5',
            trips_year=self.trips_year,
            trip_assignment=None,
            cancelled=True,
            financial_aid=0,
            registration__doc_membership=False,
        )

        # not charged because no trip assignment AND no DOC membership
        mommy.make(IncomingStudent, trips_year=self.trips_year)

        self.assertCsvReturns(
            'core:reports:charges',
            [
                {
                    'name': incoming1.name,
                    'netid': incoming1.netid,
                    'total charge': str(incoming1.compute_cost()),
                    'aid award (percentage)': '10',
                    'trip': '225.00',
                    'bus': '90.00',
                    'doc membership': '81.90',
                    'green fund': '20.00',
                    'cancellation': '',
                },
                {
                    'name': incoming2.name,
                    'netid': incoming2.netid,
                    'total charge': str(incoming2.compute_cost()),
                    'aid award (percentage)': '',
                    'trip': '250.00',
                    'bus': '',
                    'doc membership': '',
                    'green fund': '',
                    'cancellation': '',
                },
                {
                    'name': incoming3.name,
                    'netid': incoming3.netid,
                    'total charge': '91.00',
                    'aid award (percentage)': '',
                    'trip': '',
                    'bus': '',
                    'doc membership': '91.00',
                    'green fund': '',
                    'cancellation': '',
                },
                {
                    'name': incoming4.name,
                    'netid': incoming4.netid,
                    'total charge': '12.00',
                    'aid award (percentage)': '',
                    'trip': '',
                    'bus': '',
                    'doc membership': '',
                    'green fund': '12.00',
                    'cancellation': '',
                },
                {
                    'name': incoming5.name,
                    'netid': incoming5.netid,
                    'total charge': '250.00',
                    'aid award (percentage)': '',
                    'trip': '',
                    'bus': '',
                    'doc membership': '',
                    'green fund': '',
                    'cancellation': '250.00',
                },
            ],
        )

    def test_housing_report(self):
        t1 = mommy.make(
            IncomingStudent,
            name='1',
            trips_year=self.trips_year,
            trip_assignment__trips_year=self.trips_year,
            trip_assignment__section__leaders_arrive=date(2015, 1, 1),
            registration__is_fysep=True,
            registration__is_native=True,
            registration__is_international=False,
        )

        t2 = mommy.make(
            IncomingStudent, name='2', trips_year=self.trips_year, trip_assignment=None
        )

        self.assertCsvReturns(
            'core:reports:housing',
            [
                {
                    'name': t1.name,
                    'netid': t1.netid,
                    'trip': str(t1.trip_assignment),
                    'section': str(t1.trip_assignment.section.name),
                    'start date': '01/02',
                    'end date': '01/06',
                    'native': 'yes',
                    'fysep': 'yes',
                    'international': '',
                },
                {
                    'name': t2.name,
                    'netid': t2.netid,
                    'trip': '',
                    'section': '',
                    'start date': '',
                    'end date': '',
                    'native': '',
                    'fysep': '',
                    'international': '',
                },
            ],
        )

    def test_dietary_restrictions(self):
        trip = mommy.make(
            Trip, section__name='A', template__name='131', trips_year=self.trips_year
        )

        leader = mommy.make(
            Volunteer,
            trips_year=self.trips_year,
            status=Volunteer.LEADER,
            trip_assignment=trip,
            food_allergies='peaches',
            dietary_restrictions='gluten free',
            epipen=True,
        )

        croo = mommy.make(
            Volunteer,
            trips_year=self.trips_year,
            status=Volunteer.CROO,
            food_allergies='peaches',
            dietary_restrictions='gluten free',
            epipen=False,
        )

        neither = mommy.make(
            Volunteer, trips_year=self.trips_year, status=Volunteer.PENDING
        )

        reg = mommy.make(
            Registration,
            trips_year=self.trips_year,
            food_allergies='peaches',
            dietary_restrictions='gluten free',
            epipen=True,
            trippee__trip_assignment=trip,
        )

        self.assertCsvReturns(
            'core:reports:dietary',
            [
                {
                    'name': croo.applicant.name,
                    'section': '',
                    'trip': '',
                    'role': 'CROO',
                    'netid': croo.applicant.netid,
                    'food allergies': croo.food_allergies,
                    'dietary restrictions': croo.dietary_restrictions,
                    'epipen': 'No',
                },
                {
                    'name': leader.applicant.name,
                    'section': 'A',
                    'trip': '131',
                    'role': 'LEADER',
                    'netid': leader.applicant.netid,
                    'food allergies': leader.food_allergies,
                    'dietary restrictions': leader.dietary_restrictions,
                    'epipen': 'Yes',
                },
                {
                    'name': reg.name,
                    'section': 'A',
                    'trip': '131',
                    'role': 'TRIPPEE',
                    'netid': reg.user.netid,
                    'food allergies': 'peaches',
                    'dietary restrictions': 'gluten free',
                    'epipen': 'Yes',
                },
            ],
        )

    def test_medical_info(self):
        trip = mommy.make(
            Trip, trips_year=self.trips_year, section__name='A', template__name='131'
        )

        reg = mommy.make(
            Registration,
            trips_year=self.trips_year,
            trippee__trip_assignment=trip,
            food_allergies='peaches',
            dietary_restrictions='gluten free',
            medical_conditions='none',
            epipen=True,
            needs='many',
        )

        leader = mommy.make(
            Volunteer,
            trips_year=self.trips_year,
            status=Volunteer.LEADER,
            trip_assignment=trip,
            food_allergies='peaches',
            dietary_restrictions='gluten free',
            epipen=True,
            medical_conditions='none',
            needs='nada',
        )

        croo = mommy.make(
            Volunteer,
            trips_year=self.trips_year,
            status=Volunteer.CROO,
            food_allergies='peaches',
            dietary_restrictions='vegan',
            epipen=False,
            medical_conditions='',
            needs='zilch',
        )

        neither = mommy.make(
            Volunteer, trips_year=self.trips_year, status=Volunteer.PENDING
        )

        self.assertCsvReturns(
            'core:reports:medical',
            [
                {
                    'name': croo.applicant.name,
                    'section': '',
                    'trip': '',
                    'role': 'CROO',
                    'netid': croo.applicant.netid,
                    'medical conditions': '',
                    'needs': 'zilch',
                    'food allergies': 'peaches',
                    'dietary restrictions': 'vegan',
                    'epipen': 'No',
                },
                {
                    'name': leader.applicant.name,
                    'section': 'A',
                    'trip': '131',
                    'role': 'LEADER',
                    'netid': leader.applicant.netid,
                    'medical conditions': 'none',
                    'needs': 'nada',
                    'food allergies': leader.food_allergies,
                    'dietary restrictions': leader.dietary_restrictions,
                    'epipen': 'Yes',
                },
                {
                    'name': reg.name,
                    'section': 'A',
                    'trip': '131',
                    'role': 'TRIPPEE',
                    'netid': reg.user.netid,
                    'medical conditions': 'none',
                    'needs': 'many',
                    'food allergies': 'peaches',
                    'dietary restrictions': 'gluten free',
                    'epipen': 'Yes',
                },
            ],
        )

    def test_doc_memberships(self):
        reg = mommy.make(Registration, trips_year=self.trips_year, doc_membership=True)

        other_reg = mommy.make(
            Registration, trips_year=self.trips_year, doc_membership=False
        )

        self.assertCsvReturns(
            'core:reports:doc_members',
            [{'name': reg.user.name, 'netid': reg.user.netid, 'email': reg.user.email}],
        )

    def test_foodboxes(self):
        trip = mommy.make(Trip, trips_year=self.trips_year)

        mommy.make(IncomingStudent, 3, trips_year=self.trips_year)

        self.assertCsvReturns(
            'core:reports:foodboxes',
            [
                {
                    'trip': str(trip),
                    'section': trip.section.name,
                    'size': str(trip.size),
                    'full box': '1',
                    'half box': '1' if trip.half_foodbox else '',
                    'supplement': '1' if trip.supp_foodbox else '',
                    'bagels': str(trip.bagels),
                }
            ],
        )

    def test_external_bus_requests(self):
        reg1 = mommy.make(
            Registration,
            trips_year=self.trips_year,
            name='a',
            bus_stop_round_trip__trips_year=self.trips_year,
        )

        reg2 = mommy.make(
            Registration,
            trips_year=self.trips_year,
            name='b',
            bus_stop_to_hanover__trips_year=self.trips_year,
            bus_stop_from_hanover__trips_year=self.trips_year,
        )

        no_bus_request = mommy.make(Registration, trips_year=self.trips_year)

        self.assertCsvReturns(
            'core:reports:bus_stops',
            [
                {
                    'name': reg1.user.name,
                    'preferred name': reg1.name,
                    'netid': reg1.user.netid,
                    'requested bus round trip': reg1.bus_stop_round_trip.name,
                    'requested bus to hanover': '',
                    'requested bus from hanover': '',
                },
                {
                    'name': reg2.user.name,
                    'preferred name': reg2.name,
                    'netid': reg2.user.netid,
                    'requested bus round trip': '',
                    'requested bus to hanover': reg2.bus_stop_to_hanover.name,
                    'requested bus from hanover': reg2.bus_stop_from_hanover.name,
                },
            ],
        )

    def test_external_bus_riders(self):
        section = mommy.make(Section, trips_year=self.trips_year)

        bus = mommy.make(
            ExternalBus,
            section=section,
            route__category=Route.EXTERNAL,
            trips_year=self.trips_year,
        )

        s1 = mommy.make(
            IncomingStudent,
            trips_year=self.trips_year,
            trip_assignment__section=section,
            name='1',
            bus_assignment_round_trip__route=bus.route,
        )

        s2 = mommy.make(
            IncomingStudent,
            trips_year=self.trips_year,
            trip_assignment__section=section,
            name='2',
            bus_assignment_to_hanover__route=bus.route,
        )

        s3 = mommy.make(
            IncomingStudent,
            trips_year=self.trips_year,
            trip_assignment__section=section,
            name='3',
            bus_assignment_from_hanover__route=bus.route,
        )

        no_bus = mommy.make(
            Registration, trips_year=self.trips_year, trip_assignment__section=section
        )

        self.assertCsvReturns(
            'core:reports:bus_riders',
            url_kwargs={'bus_pk': bus.pk},
            target=[
                {
                    'name': '1',
                    'netid': s1.netid,
                    'phone': s1.phone,
                    'email': s1.email,
                    'blitz': s1.blitz,
                    'to hanover': 'yes',
                    'from hanover': 'yes',
                },
                {
                    'name': '2',
                    'netid': s2.netid,
                    'phone': s2.phone,
                    'email': s2.email,
                    'blitz': s2.blitz,
                    'to hanover': 'yes',
                    'from hanover': '',
                },
                {
                    'name': '3',
                    'netid': s3.netid,
                    'phone': s3.get_phone_number(),
                    'email': s3.email,
                    'blitz': s3.blitz,
                    'to hanover': '',
                    'from hanover': 'yes',
                },
            ],
        )

    def test_gear_requests(self):
        gear1 = mommy.make(Gear, trips_year=self.trips_year)
        gear2 = mommy.make(Gear, trips_year=self.trips_year)
        request1 = mommy.make(
            GearRequest,
            trips_year=self.trips_year,
            incoming_student__trips_year=self.trips_year,
            additional='teddy bear',
        )
        request1.gear.set([gear1])
        request2 = mommy.make(
            GearRequest,
            trips_year=self.trips_year,
            volunteer__trips_year=self.trips_year,
            volunteer__status=Volunteer.LEADER,
        )
        request2.gear.set([gear2])

        self.assertCsvReturns(
            'core:reports:gear_requests',
            [
                {
                    'name': str(request1.incoming_student),
                    'email': request1.incoming_student.email,
                    'role': 'TRIPPEE',
                    gear1.name: 'yes',
                    gear2.name: '',
                    'additional': 'teddy bear',
                },
                {
                    'name': str(request2.volunteer),
                    'email': request2.volunteer.applicant.email,
                    'role': 'LEADER',
                    gear1.name: '',
                    gear2.name: 'yes',
                    'additional': '',
                },
            ],
        )


class TShirtCountTestCase(FytTestCase):
    def setUp(self):
        self.init_trips_year()

    def test_tshirt_count_leaders(self):
        mommy.make(
            Volunteer,
            trips_year=self.trips_year,
            status=Volunteer.LEADER,
            trip_assignment__trips_year=self.trips_year,
            tshirt_size=S,
        )
        target = {XS: 0, S: 1, M: 0, L: 0, XL: 0, XXL: 0}
        self.assertEqual(target, leader_tshirts(self.trips_year))

    def test_tshirt_count_croos(self):
        mommy.make(
            Volunteer, trips_year=self.trips_year, status=Volunteer.CROO, tshirt_size=M
        )

        target = {XS: 0, S: 0, M: 1, L: 0, XL: 0, XXL: 0}
        self.assertEqual(target, croo_tshirts(self.trips_year))

    def test_tshirt_count_trippees(self):
        mommy.make(Registration, trips_year=self.trips_year, tshirt_size=L)
        target = {XS: 0, S: 0, M: 0, L: 1, XL: 0, XXL: 0}
        self.assertEqual(target, trippee_tshirts(self.trips_year))
