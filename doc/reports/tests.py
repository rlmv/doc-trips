import io
import csv
import tempfile
import unittest
from datetime import date

from django.core.urlresolvers import reverse
from model_mommy import mommy

from doc.test.testcases import WebTestCase, TripsTestCase
from doc.applications.tests import ApplicationTestMixin
from doc.applications.models import GeneralApplication
from doc.incoming.models import Registration, IncomingStudent
from doc.trips.models import Trip
from doc.core.models import Settings
from doc.utils.choices import YES, NO, S, M, L, XL
from doc.reports.views import leader_tshirts, croo_tshirts, trippee_tshirts


def save_and_open_csv(resp):
    """ 
    Save the file content return by response and
    open a CSV reader object over the saved file.
    """
    f = tempfile.NamedTemporaryFile()
    f.write(resp.content)
    f = open(f.name)  # open in non-binary mode
    return csv.DictReader(f)
    

class ReportViewsTestCase(WebTestCase, ApplicationTestMixin):

    def assertStopsIteration(self, iter):
        with self.assertRaises(StopIteration):
            next(iter)

    def test_volunteer_csv(self):
        trips_year = self.init_current_trips_year()
        application = self.make_application(trips_year=trips_year)
        non_applicant = self.make_application(trips_year=trips_year)
        non_applicant.croo_supplement.document = ''
        non_applicant.croo_supplement.save()
        non_applicant.leader_supplement.document = ''
        non_applicant.leader_supplement.save()
        res = self.app.get(reverse('db:reports:all_apps',
                                   kwargs={'trips_year': trips_year}),
                           user=self.mock_director())
        self.assertTrue(res['Content-Disposition'].startswith('attachment; filename="'))
        rows = list(save_and_open_csv(res))
        row = rows[0]
        self.assertEqual(row['name'], application.applicant.name)
        self.assertEqual(row['netid'], application.applicant.netid)
        self.assertEqual(len(rows), 1)
    
    def test_charges_report(self):
        trips_year = self.init_trips_year()
        mommy.make(Settings, doc_membership_cost=91, trips_cost=250)
        # incoming student to be charged:
        incoming1 = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment__trips_year=trips_year,  # force trip to exist
            bus_assignment_round_trip__cost_round_trip=37,
            financial_aid=15,
            registration__doc_membership=YES,
            registration__green_fund_donation=20
        )
        # another, without a registration
        incoming2 = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment__trips_year=trips_year,  # ditto
            financial_aid=0
        )
        # another with no trip but with doc membership
        incoming3 = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=None,
            financial_aid=0,
            registration__doc_membership=YES
        )
        # another with no trip, no membership, but green fund donation
        incoming4 = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=None,
            financial_aid=0,
            registration__doc_membership=NO,
            registration__green_fund_donation=12
        )
        # last-minute cancellation
        incoming5 = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=None,
            cancelled=True,
            financial_aid=0,
            registration__doc_membership=NO,
        )

        # not charged because no trip assignment AND no DOC membership
        mommy.make(IncomingStudent, trips_year=trips_year)

        url = reverse('db:reports:charges', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.mock_director())

        rows = list(save_and_open_csv(resp))
        target = [{
            'name': incoming1.name,
            'netid': incoming1.netid,
            'total charge': str(incoming1.compute_cost()),
            'aid award (percentage)': '15',
            'trip': '250',
            'bus': '37',
            'doc membership': '91',
            'green fund donation': '20',
        }, {
            'name': incoming2.name,
            'netid': incoming2.netid,
            'total charge': str(incoming2.compute_cost()),
            'aid award (percentage)': '',
            'trip': '250',
            'bus': '',
            'doc membership': '',
            'green fund donation': '',
        }, {
            'name': incoming3.name,
            'netid': incoming3.netid,
            'total charge': '91.0',
            'aid award (percentage)': '',
            'trip': '',
            'bus': '',
            'doc membership': '91',
            'green fund donation': '',
        }, {
            'name': incoming4.name,
            'netid': incoming4.netid,
            'total charge': '12.0',
            'aid award (percentage)': '',
            'trip': '',
            'bus': '',
            'doc membership': '',
            'green fund donation': '12',
        }, {
            'name': incoming5.name,
            'netid': incoming5.netid,
            'total charge': '250.0',
            'aid award (percentage)': '',
            'trip': '250',
            'bus': '',
            'doc membership': '',
            'green fund donation': '',
        }]
        self.assertEqual(rows, target)

    def test_housing_report(self):
        trips_year = self.init_trips_year()
        t1 = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment__trips_year=trips_year,
            trip_assignment__section__leaders_arrive=date(2015, 1, 1),
            registration__is_fysep=YES,
            registration__is_native=YES,
            registration__is_international=NO
        )
        t2 = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=None
        )
        url = reverse('db:reports:housing', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.mock_director())
        
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


    def test_dietary_restrictions(self):
        trips_year = self.init_trips_year()
        trip = mommy.make(
            Trip,
            trips_year=trips_year
        )
        reg = mommy.make(
            Registration,
            trips_year=trips_year,
            medical_conditions='none',
            allergies='peaches',
            allergen_information='I go into shock',
            allergy_severity=1,
            dietary_restrictions='gluten free',
            allergy_reaction='hives',
        )
        inc = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=trip,
            registration=reg,
        )
        url = reverse('db:reports:dietary', kwargs={'trips_year': trips_year})
        resp  = self.app.get(url, user=self.mock_director())

        rows = list(save_and_open_csv(resp))
        target = [{
            'name': reg.name,
            'netid': reg.user.netid,
            'section': trip.section.name,
            'trip': str(trip),
            'allergies': 'peaches',
            'allergen information': 'I go into shock',
            'food allergy reaction': 'hives',
            'food allergy severity (1-5)': '1',
            'dietary restrictions': 'gluten free',
            'medical conditions': 'none',
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
            medical_conditions='none',
            allergies='peaches',
            allergen_information='I go into shock',
            allergy_severity=1,
            dietary_restrictions='gluten free',
            allergy_reaction='hives',
            epipen='YES',
            needs='many',
        )
        inc = mommy.make(
            IncomingStudent,
            trips_year=trips_year,
            trip_assignment=trip,
            registration=reg,
        )
        url = reverse('db:reports:medical', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.mock_director())

        rows = list(save_and_open_csv(resp))
        target = [{
            'name': reg.name,
            'netid': reg.user.netid,
            'trip': str(trip),
            'medical conditions': 'none',
            'allergies': 'peaches',
            'allergen information': 'I go into shock',
            'food allergy reaction': 'hives',
            'food allergy severity (1-5)': '1',
            'epipen': 'YES',
            'needs': 'many',
        }]
        self.assertEqual(rows, target)

    def test_doc_memberships(self):
        trips_year = self.init_trips_year()
        reg = mommy.make(
            Registration,
            trips_year=trips_year,
            doc_membership=YES
        )
        other_reg = mommy.make(
            Registration,
            trips_year=trips_year,
            doc_membership=NO
        )
        url = reverse('db:reports:doc_members', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.mock_director())

        target = [{
            'name': reg.user.name,
            'netid': reg.user.netid,
            'email': reg.user.email
        }]
        self.assertEqual(list(save_and_open_csv(resp)), target)


    def test_volunteer_dietary_restrictions(self):
        trips_year = self.init_trips_year()

        leader = mommy.make(
            GeneralApplication, trips_year=trips_year,
            status=GeneralApplication.LEADER
        )
        croo = mommy.make(
            GeneralApplication, trips_year=trips_year,
            status=GeneralApplication.CROO
        )
        neither = mommy.make(
            GeneralApplication, trips_year=trips_year,
            status=GeneralApplication.PENDING
        )
        url = reverse('db:reports:volunteer_dietary', kwargs={'trips_year': trips_year})
        resp = self.app.get(url, user=self.mock_director())
        rows = list(save_and_open_csv(resp))
        target = [{
            'name': croo.applicant.name,
            'netid': croo.applicant.netid,
            'role': GeneralApplication.CROO,
            'dietary restrictions': croo.dietary_restrictions,
            'allergen information': croo.allergen_information,
        }, {
            'name': leader.applicant.name,
            'netid': leader.applicant.netid,
            'role': GeneralApplication.LEADER,
            'dietary restrictions': leader.dietary_restrictions,
            'allergen information': leader.allergen_information,
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
        resp = self.app.get(url, user=self.mock_director())

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


class TShirtCountTestCase(TripsTestCase):
    
    def test_tshirt_count_leaders(self):
        trips_year = self.init_trips_year()
        mommy.make(
            GeneralApplication,
            trips_year=trips_year,
            status=GeneralApplication.LEADER,
            assigned_trip__trips_year=trips_year,
            tshirt_size=S
        )
        target = {
            S: 1, M: 0, L: 0, XL: 0
        }
        self.assertEqual(target, leader_tshirts(trips_year))
        
    def test_tshirt_count_croos(self):
        trips_year = self.init_trips_year()
        mommy.make(
            GeneralApplication,
            trips_year=trips_year,
            status=GeneralApplication.CROO,
            tshirt_size=M
        )
        target = {
            S: 0, M: 1, L: 0, XL: 0
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
            S: 0, M: 0, L: 1, XL: 0
        }
        self.assertEqual(target, trippee_tshirts(trips_year))
        

        
