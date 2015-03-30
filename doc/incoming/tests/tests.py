import os

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

       
FILE = os.path.join(os.path.dirname(__file__), 'incoming_students.csv')

class ImportIncomingStudentsTestCase(TripsYearTestCase):

    
    def test_create_from_csv(self):

        trips_year = self.init_current_trips_year().pk
        
        with open(FILE) as f:
            (created, existing) = IncomingStudent.objects.create_from_csv_file(f, trips_year)

        self.assertEqual(set(['id_1', 'id_2']), set(created))
        self.assertEqual(existing, [])
        
        # are student objects created?
        IncomingStudent.objects.get(netid='id_1')
        IncomingStudent.objects.get(netid='id_2')


    def test_ignore_existing_students(self):
        
        trips_year = self.init_current_trips_year().pk
        with open(FILE) as f:
            (created, existing) = IncomingStudent.objects.create_from_csv_file(f, trips_year)

        with open(FILE) as f:
            (created, existing) = IncomingStudent.objects.create_from_csv_file(f, trips_year)

        self.assertEqual(set(['id_1', 'id_2']), set(existing))
        self.assertEqual(created, [])
        
        
