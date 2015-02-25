
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase as TripsTestCase, WebTestCase
from doc.applications.models import LeaderSupplement, CrooSupplement
from doc.timetable.models import Timetable


class ApplicationAccessTestCase(WebTestCase):

    def setUp(self):
        self.init_current_trips_year()

    def test_anonymous_user_does_not_crash_application(self):
        
        self.app.get(reverse('applications:apply'))


class ApplicationFormTestCase(WebTestCase):

    csrf_checks = False
    
    def setUp(self):
        self.init_current_trips_year()

    def test_file_uploads_dont_overwrite_each_other(self):
        # TODO / scrap
        
        self.mock_user()
        mommy.make('ApplicationInformation', trips_year=self.current_trips_year)

        timetable = Timetable.objects.timetable()
        timetable.applications_open = datetime.min
        timetable.applications_close = datetime.max
        timetable.save()

        res = self.app.get(reverse('applications:apply'), user=self.user)
        print(res)
        print(res.form)
                             
        
        
        

        

    
