
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from model_mommy import mommy

from test.fixtures import TripsYearTestCase as TripsTestCase, WebTestCase
from applications.models import LeaderSupplement, CrooSupplement


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

        self.mock_user()

        timetable = Timetable.objects.timetable()
        timetable.applications_open = datetime.min
        timetable.applications_close = datetime.max
        timetable.save()

        application = mommy.make('GeneralApplication', applicant=self.user
)
        leader_app = mommy.make('LeaderSupplement', application=application, document='')
        croo_app = mommy.make('CrooSupplement', application=application, document='')
        
        res = self.app.get(reverse('applications:continue'), user=self.user)
        print(res)
        from webtest import Upload
        res.form['document'] = Upload('test.py')
        
        res = res.form.submit()
        
        self.assertNotEquals(LeaderSupplement.objects.get(pk=leader_app.pk).document, 
                             CrooSupplement.objects.get(pk=croo_app.pk).document)
                             
        
        
        

        

    
