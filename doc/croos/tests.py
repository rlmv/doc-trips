from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase as TripsTestCase
from doc.croos.models import Croo
from doc.applications.models import GeneralApplication

class CrooModelTestCase(TripsTestCase):
    
    def test_safety_leads(self):
        trips_year = self.init_current_trips_year()
        croo = mommy.make(Croo, trips_year=trips_year)
        CROO = GeneralApplication.CROO
        safety_lead = mommy.make(GeneralApplication, trips_year=trips_year, 
                                 safety_lead=True, status=CROO, assigned_croo=croo)
        other_member = mommy.make(GeneralApplication, trips_year=trips_year,
                                  safety_lead=False, status=CROO, assigned_croo=croo)
        self.assertEqual([safety_lead], list(croo.safety_leads()))
        
