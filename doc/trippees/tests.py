
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase
from doc.trippees.models import TrippeeRegistration, Trippee

class TrippeeModelsTestCase(TripsYearTestCase):

    def setUp(self):
        pass
    
    def test_signal_creates_Trippee_for_TrippeeRegistration(self):
        
        user = self.mock_user()
        trips_year = self.init_current_trips_year()
        reg = mommy.make(TrippeeRegistration, trips_year=trips_year, user=user)
        
        created_trippee = Trippee.objects.get(registration=reg)
        self.assertEqual(created_trippee.trips_year, trips_year)
        self.assertEqual(created_trippee.user, user)
        self.assertEqual(created_trippee.registration, reg)
        
        
