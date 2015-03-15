
from django.db.models import ProtectedError
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase
from doc.transport.models import Stop, Route


class TransportModelTestCase(TripsYearTestCase):
    
    def test_stop_is_protected_on_route_fk_deletion(self):

        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year)
        stop = mommy.make(Stop, route=route, trips_year=trips_year)
        with self.assertRaises(ProtectedError):
            route.delete()

