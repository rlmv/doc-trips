
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from model_mommy import mommy

from test.fixtures import TripsYearTestCase as TripsTestCase
from croos.models import CrooApplication, Croo

class CrooApplicationModelTestCase(TripsTestCase):

    def setUp(self):
        self.init_current_trips_year()

    def test_pending_croo_assignment_raises_exception(self):
        
        croo = mommy.make(Croo)
        applicant = mommy.make(get_user_model())
        app = mommy.prepare(CrooApplication, status=CrooApplication.PENDING,
                            assigned_croo=croo, trips_year=self.current_trips_year, 
                            applicant=applicant)
        
        with self.assertRaises(ValidationError):
            app.full_clean()
                            
