from django.core.exceptions import ObjectDoesNotExist
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase
from doc.trippees.models import TrippeeRegistration, Trippee, CollegeInfo

class TrippeeModelsTestCase(TripsYearTestCase):

    def setUp(self):
        pass
    
    def test_creating_CollegeInfo_automatically_creates_Trippee(self):
        
        trips_year = self.init_current_trips_year()
        info = mommy.make(CollegeInfo, trips_year=trips_year)

        created_trippee = Trippee.objects.get(info=info)
        self.assertEqual(created_trippee.trips_year, trips_year)
    
    def test_creating_Registration_automatically_links_to_existing_Trippee(self):
        
        user = self.mock_incoming_student()
        trips_year = self.init_current_trips_year()
        # make existing info for user with did
        info = mommy.make(CollegeInfo, did=user.did, trips_year=trips_year)
        
        reg = mommy.make(TrippeeRegistration, trips_year=trips_year, user=user)
        self.assertEqual(reg.trippee.info, info)

    def test_creating_Registration_without_incoming_info_does_nothing(self):
 
        user = self.mock_incoming_student()
        trips_year = self.init_current_trips_year()
        
        reg = mommy.make(TrippeeRegistration, trips_year=trips_year, user=user)

        with self.assertRaises(ObjectDoesNotExist):
            reg.trippee


