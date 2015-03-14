from django.core.exceptions import ObjectDoesNotExist
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase
from doc.trippees.models import Registration, IncomingStudent

class IncomingStudentModelsTestCase(TripsYearTestCase):

    def setUp(self):
        pass
    
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

        



