import csv
import tempfile
from collections import OrderedDict
from datetime import date

from django.core.urlresolvers import reverse
from model_mommy import mommy

from fyt.applications.models import Question, Volunteer
from fyt.applications.tests import ApplicationTestMixin
from fyt.croos.models import Croo
from fyt.incoming.models import IncomingStudent, Registration, Settings
from fyt.reports.views import croo_tshirts, leader_tshirts, trippee_tshirts
from fyt.test import FytTestCase
from fyt.transport.models import Stop
from fyt.trips.models import Section, Trip, TripType
from fyt.utils.choices import L, M, S, XL, XS, XXL


def save_and_open_csv(resp):
    """
    Save the file content return by response and
    open a CSV reader object over the saved file.
    """
    f = tempfile.NamedTemporaryFile()
    f.write(resp.content)
    f = open(f.name)  # open in non-binary mode
    return csv.DictReader(f)


class ReportViewsTestCase(FytTestCase, ApplicationTestMixin):

    maxDiff = None

    def assertStopsIteration(self, iter):
        with self.assertRaises(StopIteration):
            next(iter)

    def assertViewReturns(self, urlpattern, target):
        """
        Test a view by visiting it with director priveleges and
        comparing returned csv to ``target``.

        ``urlpattern`` is a reversable pattern,
        ``target`` is a list of ``dicts``
        """
        url = reverse(urlpattern, kwargs={'trips_year': self.trips_year})
        resp = self.app.get(url, user=self.make_director())

        self.assertTrue(resp['Content-Disposition'].startswith(
            'attachment; filename="'))
        self.assertEqual([dict(r) for r in save_and_open_csv(resp)], target)

    def test_volunteer_csv(self):
        trips_year = self.init_trips_year()
        question = mommy.make(Question, trips_year=trips_year)
        app = self.make_application(trips_year=trips_year)
        app.croo_willing = False
        app.save()
        app.answer_question(question, 'An answer')
        app.add_score(self.make_grader(), 4)
        app.add_score(self.make_directorate(), 5)
        app.add_score(self.make_tlt(), 4)

        target = [{
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
            'avg score': '4.3',
            'score 1': '4',
            'score 2': '5',
            'score 3': '4',
        }]

        self.assertViewReturns('db:reports:all_apps', target)

    def test_trip_leader_csv(self):
        trips_year = self.init_trips_year()
        trip = mommy.make(Trip, trips_year=trips_year)
        leader = self.make_application(
            trips_year=trips_year,
            status=Volunteer.LEADER,
            assigned_trip=trip
        )
        not_leader = self.make_application(trips_year=trips_year)

        url = reverse('db:reports:leaders', kwargs={'trips_year': trips_year})
        rows = list(save_and_open_csv(self.app.get(url, user=self.make_director())))
        target = [{
            'name': leader.name,
            'netid': leader.applicant.netid,
            'trip': str(trip),
            'section': trip.section.name
        }]

        self.assertEqual(rows, target)

    def test_croo_members_csv(self):
        trips_year = self.init_trips_year()
        croo = mommy.make(Croo, trips_year=trips_year)
        crooling = self.make_application(
            trips_year=trips_year,
            status=Volunteer.CROO,
            assigned_croo=croo
        )
        not_croo = self.make_application(trips_year=trips_year)

        url = reverse('db:reports:croo_members', kwargs={'trips_year': trips_year})
        rows = list(save_and_open_csv(self.app.get(url, user=self.make_director())))
        target = [{
            'name': crooling.name,
            'netid': crooling.applicant.netid,
            'croo': str(crooling.assigned_croo)
        }]
        self.assertEqual(rows, target)

    def test_trippees_csv(self):
        trips_year = self.init_trips_year()
        trippee = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=mommy.make(Trip)
        )
        not_trippee = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=None
        )
        target = [{
            'name': trippee.name,
            'netid': trippee.netid.upper()
        }]
        self.assertViewReturns('db:reports:trippees', target)

    def test_registrations_csv(self):
        trips_year = self.init_trips_year()
        r = mommy.make(
            Registration,
            trips_year=trips_year,
            name='Bob',
            gender='male',
        )
        section = mommy.make(Section, trips_year=trips_year, name='A')
        r.set_section_preference(section, 'PREFER')
        triptype = mommy.make(TripType, trips_year=trips_year, name='Hiking 3')
        r.set_triptype_preference(triptype, 'AVAILABLE')

        target = [{
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
        }]
        self.assertViewReturns('db:reports:registrations', target)

    def test_charges_report(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, trips_year=trips_year, doc_membership_cost=91, trips_cost=250)
        # incoming student to be charged:
        incoming1 = mommy.make(
            IncomingStudent,
            name='1',
            trips_year=trips_year,
            trip_assignment__trips_year=trips_year,  # force trip to exist
            bus_assignment_round_trip__cost_round_trip=100,
            financial_aid=10,
            registration__doc_membership=True,
            registration__green_fund_donation=20
        )
        # another, without a registration
        incoming2 = mommy.make(
            IncomingStudent,
            name='2',
            trips_year=trips_year,
            trip_assignment__trips_year=trips_year,  # ditto
            financial_aid=0
        )
        # another with no trip but with doc membership
        incoming3 = mommy.make(
            IncomingStudent,
            name='3',
            trips_year=trips_year,
            trip_assignment=None,
            financial_aid=0,
            registration__doc_membership=True
        )
        # another with no trip, no membership, but green fund donation
        incoming4 = mommy.make(
            IncomingStudent,
            name='4',
            trips_year=trips_year,
            trip_assignment=None,
            financial_aid=0,
            registration__doc_membership=False,
            registration__green_fund_donation=12
        )
        # last-minute cancellation
        incoming5 = mommy.make(
            IncomingStudent,
            name='5',
            trips_year=trips_year,
            trip_assignment=None,
            cancelled=True,
            financial_aid=0,
            registration__doc_membership=False,
        )

        # not charged because no trip assignment AND no DOC membership
        mommy.make(IncomingStudent, trips_year=trips_year)

        url = reverse('db:reports:charges', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.make_director())

        rows = list(save_and_open_csv(resp))
        target = [{
            'name': incoming1.name,
            'netid': incoming1.netid,
            'total charge': str(incoming1.compute_cost()),
            'aid award (percentage)': '10',
            'trip': '225.00',
            'bus': '90.00',
            'doc membership': '81.90',
            'green fund': '20.00',
            'cancellation': ''
        }, {
            'name': incoming2.name,
            'netid': incoming2.netid,
            'total charge': str(incoming2.compute_cost()),
            'aid award (percentage)': '',
            'trip': '250.00',
            'bus': '',
            'doc membership': '',
            'green fund': '',
            'cancellation': ''
        }, {
            'name': incoming3.name,
            'netid': incoming3.netid,
            'total charge': '91.00',
            'aid award (percentage)': '',
            'trip': '',
            'bus': '',
            'doc membership': '91.00',
            'green fund': '',
            'cancellation': ''
        }, {
            'name': incoming4.name,
            'netid': incoming4.netid,
            'total charge': '12.00',
            'aid award (percentage)': '',
            'trip': '',
            'bus': '',
            'doc membership': '',
            'green fund': '12.00',
            'cancellation': ''
        }, {
            'name': incoming5.name,
            'netid': incoming5.netid,
            'total charge': '250.00',
            'aid award (percentage)': '',
            'trip': '',
            'bus': '',
            'doc membership': '',
            'green fund': '',
            'cancellation': '250.00'
        }]
        self.assertEqual(rows, target)

    def test_housing_report(self):
        trips_year = self.init_trips_year()
        t1 = mommy.make(
            IncomingStudent,
            name='1',
            trips_year=trips_year,
            trip_assignment__trips_year=trips_year,
            trip_assignment__section__leaders_arrive=date(2015, 1, 1),
            registration__is_fysep=True,
            registration__is_native=True,
            registration__is_international=False
        )
        t2 = mommy.make(
            IncomingStudent,
            name='2',
            trips_year=trips_year,
            trip_assignment=None
        )
        url = reverse('db:reports:housing', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.make_director())

        rows = list(save_and_open_csv(resp))
        target = [{
            'name': t1.name,
            'netid': t1.netid,
            'trip': str(t1.trip_assignment),
            'section': str(t1.trip_assignment.section.name),
            'start date': '01/02',
            'end date': '01/06',
            'native': 'yes',
            'fysep': 'yes',
            'international': ''
        }, {
            'name': t2.name,
            'netid': t2.netid,
            'trip': '',
            'section': '',
            'start date': '',
            'end date': '',
            'native': '',
            'fysep': '',
            'international': '',
        }]
        self.assertEqual(rows, target)


    def test_dietary_restrictions(self):
        trips_year = self.init_trips_year()
        trip = mommy.make(
            Trip,
            trips_year=trips_year
        )
        reg = mommy.make(
            Registration,
            trips_year=trips_year,
            food_allergies='peaches',
            dietary_restrictions='gluten free',
            epipen=True,
        )
        inc = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=trip,
            registration=reg,
        )
        url = reverse('db:reports:dietary', kwargs={'trips_year': trips_year})
        resp  = self.app.get(url, user=self.make_director())

        rows = list(save_and_open_csv(resp))
        target = [{
            'name': reg.name,
            'netid': reg.user.netid,
            'section': trip.section.name,
            'trip': str(trip),
            'food allergies': 'peaches',
            'dietary restrictions': 'gluten free',
            'epipen': 'Yes',
        }]
        self.assertEqual(rows, target)

    def test_medical_info(self):
        trips_year = self.init_trips_year()
        trip = mommy.make(
            Trip,
            trips_year=trips_year
        )
        reg = mommy.make(
            Registration,
            trips_year=trips_year,
            food_allergies='peaches',
            dietary_restrictions='gluten free',
            medical_conditions='none',
            epipen=True,
            needs='many',
        )
        inc = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=trip,
            registration=reg,
        )
        url = reverse('db:reports:medical', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.make_director())

        rows = list(save_and_open_csv(resp))
        target = [{
            'name': reg.name,
            'netid': reg.user.netid,
            'section': trip.section.name,
            'trip': str(trip),
            'medical conditions': 'none',
            'needs': 'many',
            'food allergies': 'peaches',
            'dietary restrictions': 'gluten free',
            'epipen': 'Yes',
        }]
        self.assertEqual(rows, target)

    def test_doc_memberships(self):
        trips_year = self.init_trips_year()
        reg = mommy.make(
            Registration,
            trips_year=trips_year,
            doc_membership=True
        )
        other_reg = mommy.make(
            Registration,
            trips_year=trips_year,
            doc_membership=False
        )
        url = reverse('db:reports:doc_members', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.make_director())

        target = [{
            'name': reg.user.name,
            'netid': reg.user.netid,
            'email': reg.user.email
        }]
        self.assertEqual(list(save_and_open_csv(resp)), target)


    def test_volunteer_dietary_restrictions(self):
        trips_year = self.init_trips_year()

        leader = mommy.make(
            Volunteer, trips_year=trips_year,
            status=Volunteer.LEADER,
            assigned_trip=mommy.make(Trip, trips_year=trips_year),
            food_allergies='peaches',
            dietary_restrictions='gluten free',
            epipen=True,
        )
        croo = mommy.make(
            Volunteer, trips_year=trips_year,
            status=Volunteer.CROO,
            food_allergies='peaches',
            dietary_restrictions='gluten free',
            epipen=False
        )
        neither = mommy.make(
            Volunteer, trips_year=trips_year,
            status=Volunteer.PENDING
        )
        url = reverse('db:reports:volunteer_dietary', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.make_director())
        rows = list(save_and_open_csv(resp))
        target = [{
            'name': croo.applicant.name,
            'netid': croo.applicant.netid,
            'role': Volunteer.CROO,
            'trip': '',
            'food allergies': croo.food_allergies,
            'dietary restrictions': croo.dietary_restrictions,
            'epipen': 'No'
        }, {
            'name': leader.applicant.name,
            'netid': leader.applicant.netid,
            'role': Volunteer.LEADER,
            'trip': str(leader.assigned_trip),
            'food allergies': leader.food_allergies,
            'dietary restrictions': leader.dietary_restrictions,
            'epipen': 'Yes'
        }]
        self.assertEqual(rows, target)


    def test_foodboxes(self):
        trips_year = self.init_trips_year()
        trip = mommy.make(
            Trip,
            trips_year=trips_year,
        )
        mommy.make(
            IncomingStudent, 3,
            trips_year=trips_year
        )
        url = reverse('db:reports:foodboxes', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.make_director())

        rows = list(save_and_open_csv(resp))
        target = [{
            'trip': str(trip),
            'section': trip.section.name,
            'size': str(trip.size()),
            'full box': '1',
            'half box': '1' if trip.half_foodbox else '',
            'supplement': '1' if trip.supp_foodbox else '',
            'bagels': str(trip.bagels),
        }]
        self.assertEqual(rows, target)


    def test_external_bus(self):
        trips_year = self.init_trips_year()
        reg1 = mommy.make(
            Registration,
            trips_year=trips_year,
            name='a',
            bus_stop_round_trip=mommy.make(Stop, trips_year=trips_year)
        )
        reg2 = mommy.make(
            Registration,
            trips_year=trips_year,
            name='b',
            bus_stop_to_hanover=mommy.make(Stop, trips_year=trips_year),
            bus_stop_from_hanover=mommy.make(Stop, trips_year=trips_year)
        )
        no_bus_request = mommy.make(
            Registration,
            trips_year=trips_year
        )

        url = reverse('db:reports:bus_stops', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.make_director())

        rows = list(save_and_open_csv(resp))
        target = [{
            'name': reg1.user.name,
            'preferred name': reg1.name,
            'netid': reg1.user.netid,
            'requested bus round trip': reg1.bus_stop_round_trip.name,
            'requested bus to hanover': '',
            'requested bus from hanover': '',
        },{
            'name': reg2.user.name,
            'preferred name': reg2.name,
            'netid': reg2.user.netid,
            'requested bus round trip': '',
            'requested bus to hanover': reg2.bus_stop_to_hanover.name,
            'requested bus from hanover': reg2.bus_stop_from_hanover.name,
        }]
        self.assertEqual(rows, target)


class TShirtCountTestCase(FytTestCase):

    def test_tshirt_count_leaders(self):
        trips_year = self.init_trips_year()
        mommy.make(
            Volunteer,
            trips_year=trips_year,
            status=Volunteer.LEADER,
            assigned_trip__trips_year=trips_year,
            tshirt_size=S
        )
        target = {
            XS: 0, S: 1, M: 0, L: 0, XL: 0, XXL: 0
        }
        self.assertEqual(target, leader_tshirts(trips_year))

    def test_tshirt_count_croos(self):
        trips_year = self.init_trips_year()
        mommy.make(
            Volunteer,
            trips_year=trips_year,
            status=Volunteer.CROO,
            tshirt_size=M
        )
        target = {
            XS: 0, S: 0, M: 1, L: 0, XL: 0, XXL: 0
        }
        self.assertEqual(target, croo_tshirts(trips_year))

    def test_tshirt_count_trippees(self):
        trips_year = self.init_trips_year()
        mommy.make(
            Registration,
            trips_year=trips_year,
            tshirt_size=L
        )
        target = {
            XS:0, S: 0, M: 0, L: 1, XL: 0, XXL: 0
        }
        self.assertEqual(target, trippee_tshirts(trips_year))
