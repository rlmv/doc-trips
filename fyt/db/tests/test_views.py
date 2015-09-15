from model_mommy import mommy
 
from ..urlhelpers import reverse_detail_url, reverse_update_url, reverse_delete_url
from fyt.test import WebTestCase
from fyt.trips.models import Section


class DetailViewTestCase(WebTestCase):

    def test_urls_in_context(self):
        trips_year = self.init_trips_year()
        # test Section detail, for example
        section = mommy.make(Section, trips_year=trips_year)
        resp = self.app.get(reverse_detail_url(section), user=self.mock_director())
        self.assertEqual(resp.context['update_url'], reverse_update_url(section))
        self.assertEqual(resp.context['delete_url'], reverse_delete_url(section))
