
from django.db.models import ProtectedError
from django.core.urlresolvers import reverse
from model_mommy import mommy

from doc.test.fixtures import TripsYearTestCase, WebTestCase
from doc.transport.models import Stop, Route


class TransportModelTestCase(TripsYearTestCase):
    
    def test_stop_is_protected_on_route_fk_deletion(self):

        trips_year = self.init_current_trips_year()
        route = mommy.make(Route, trips_year=trips_year)
        stop = mommy.make(Stop, route=route, trips_year=trips_year)
        with self.assertRaises(ProtectedError):
            route.delete()


class ManagersTestCase(TripsYearTestCase):

    def test_external(self):
        
        trips_year = self.init_current_trips_year()
        external_stop = mommy.make(Stop, trips_year=trips_year, category='EXTERNAL')
        internal_stop = mommy.make(Stop, trips_year=trips_year, category='INTERNAL')
        self.assertEqual([external_stop], list(Stop.objects.external(trips_year)))


class TestViews(WebTestCase):

    def test_index_views(self):
        
        trips_year = self.init_current_trips_year()
        director = self.mock_director()
        
        names = [
            'db:stop_index',
            'db:route_index',
            'db:vehicle_index',
        ]

        for name in names:
            res = self.app.get(reverse(name, kwargs={'trips_year': trips_year}), user=director)


