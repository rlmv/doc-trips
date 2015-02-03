
from django.contrib.auth import get_user_model
from django.test import TestCase, LiveServerTestCase
from model_mommy import mommy
from django_webtest import WebTest

from db.models import TripsYear
from permissions import directors, graders


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
        self.user = get_user_model().objects.create_user(netid, netid)

        return self.user

    def mock_director(self):
        """ Create a user with director permissions, and log the user in. """

        netid = 'director'
        self.director = get_user_model().objects.create_user(netid, netid)
        self.director.groups.add(directors())
        self.director.save()

        return self.director

    def mock_grader(self):
        
        netid = 'grader'
        self.grader = get_user_model().objects.create_user(netid, netid)
                 
        self.grader.groups.add(graders())
        self.grader.save()

        return self.grader



class TripsYearTestCase(TestCase, TripsYearTestCaseUtils):
    pass


class WebTestCase(WebTest, TripsYearTestCaseUtils):
    """ 
    Can make requests without have to mock CAS 
    authentication. See django_webtest for more details.
    """ 
    pass
