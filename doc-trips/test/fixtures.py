
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
