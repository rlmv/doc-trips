
from django.contrib.auth import get_user_model
from model_mommy import mommy

from db.models import TripsYear

def init_trips_year():
    """ Initialize a current trips_year object in the test database.
    
    This should be called in the setUp() method of most TestCases, 
    otherwise the database is going to barf when there is no current
    trips_year.
    """
    trips_year = mommy.make(TripsYear, is_current=True)
    trips_year.save()

    return trips_year

def initialize_trips_year(test_case):
    
    test_case.trips_year = init_trips_year()

def mock_login(test_case):
    """ Create a mock user, and login to the test client

    Bypasses CAS authentication 
    """
    test_case.username='username'
    test_case.password='password'
    test_case.user = get_user_model().objects.create_user(username=test_case.username, password=test_case.password)
    test_case.client.login(username=test_case.username, password=test_case.password)
