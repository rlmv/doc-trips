
from django.contrib.auth import get_user_model
from django.test import TestCase, LiveServerTestCase
from model_mommy import mommy
from splinter import Browser

from db.models import TripsYear
from permissions import directors, graders


class TestCase(TestCase):
    
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

    def init_old_trips_year(self):
        self.old_trips_year = mommy.make(TripsYear, year=2013, is_current=False)
        self.old_trips_year.save()

        return self.old_trips_year

    def mock_user_login(self):
        """ 
        Create a mock user, and login to the test client

        Bypasses CAS authentication 
        """
        username='user'
        password='password'
        self.user = get_user_model().objects.create_user(username=username, password=password)
        self.client.login(username=username, password=password)

        return self.user

    def mock_director_login(self):
        """ Create a user with director permissions, and log the user in. """
        
        username='director'
        password='password'
        self.director = get_user_model().objects.create_user(username=username,
                                                              password=password)
        self.director.groups.add(directors())
        self.director.save
        
        self.client.login(username=username, password=password)
        
        return self.director


class LiveServerTestCase(LiveServerTestCase):

    def setUp(self):
        self.browser = Browser()
    
    def tearDown(self):
        self.browser.quit()
        

