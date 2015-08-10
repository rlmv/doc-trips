
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, LiveServerTestCase
from model_mommy import mommy
from django_webtest import WebTest

from doc.db.models import TripsYear
from doc.permissions import directors, graders, directorate, trip_leader_trainers, safety_leads


class TripsYearTestCaseUtils():

    def init_current_trips_year(self):
        """ 
        Initialize a current trips_year object in the test database.

        This should be called in the setUp() method of most TestCases, 
        otherwise the database is going to barf when there is no current
        trips_year.
        """
        self.trips_year = mommy.make(TripsYear, year=2014, is_current=True)
        self.current_trips_year = self.trips_year
        self.trips_year.save()

        return self.trips_year

    init_trips_year = init_current_trips_year

    def init_old_trips_year(self):
        self.old_trips_year = mommy.make(TripsYear, year=2013, is_current=False)
        self.previous_trips_year = self.old_trips_year
        self.old_trips_year.save()

        return self.old_trips_year
        
    init_previous_trips_year = init_old_trips_year

    def mock_user(self):
        """ 
        Create a mock user.
        """
        netid = 'user'
        email = netid + '@dartmouth.edu'
        self.user = get_user_model().objects.create_user(netid, netid, email)

        return self.user
        
    def mock_incoming_student(self):
        netid = 'incoming'
        name = 'incoming'
        email = netid + '@dartmouth.edu'
        did = 'incoming DID'
        self.user = get_user_model().objects.create_user(netid, name, email, did)
        
        return self.user

    def mock_director(self):
        """ 
        Create a user with director permissions, and log the user in.
        """
        netid = 'director'
        email = netid + '@dartmouth.edu'
        self.director = get_user_model().objects.create_user(netid, netid, email)
        self.director.groups.add(directors())
        self.director.save()

        return self.director

    def mock_directorate(self):
        """
        Create a user with directorate permissions, and log the user in.
        """
        netid = 'directorate'
        email = netid + '@dartmouth.edu'
        self.directorate = get_user_model().objects.create_user(netid, netid, email)
        self.directorate.groups.add(directorate())
        self.directorate.save()

        return self.directorate

    def mock_tlt(self):
        """ 
        Create a user with trip leader trainer permissions, and log the user in.
        """
        netid = 'tlt'
        email = netid + '@dartmouth.edu'
        self.tlt = get_user_model().objects.create_user(netid, netid, email)
        self.tlt.groups.add(trip_leader_trainers())
        self.tlt.save()

        return self.tlt

    def mock_grader(self):
        netid = 'grader'
        email = netid + '@dartmouth.edu'
        self.grader = get_user_model().objects.create_user(netid, netid, email)
        self.grader.groups.add(graders())
        self.grader.save()

        return self.grader

    def mock_safety_lead(self):
        netid = 'safety'
        email = netid + '@dartmouth.edu'
        self.safety_lead = get_user_model().objects.create_user(netid, netid, email)
        self.safety_lead.groups.add(safety_leads())
        self.safety_lead.save()

        return self.safety_lead

    def assertQsEqual(self, qs, values, transform=lambda x: x, ordered=False, msg=None):
        """
        Override django assertQuerysetEqual with more useful arguments.
        """
        return self.assertQuerysetEqual(qs, values, transform=transform,
                                        ordered=ordered, msg=msg)


class TripsYearTestCase(TestCase, TripsYearTestCaseUtils):
    pass
TripsTestCase = TripsYearTestCase


class WebTestCase(WebTest, TripsYearTestCaseUtils):
    """
    Can make requests without have to mock CAS 
    authentication. See django_webtest for more details.

    For some reason whitenoise's GzipManifestStaticFilesStorage doesn't
    work with WebTest. We patch it here back to the django default storage.
    """
    
    def _patch_settings(self):
        super(WebTestCase, self)._patch_settings()
        self._STATICFILES_STORAGE = settings.STATICFILES_STORAGE
        settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
        
    def _unpatch_settings(self):
        super(WebTestCase, self)._unpatch_settings()
        settings.STATICFILES_STORAGE = self._STATICFILES_STORAGE
