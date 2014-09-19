
from django.test.utils import override_settings
from django.conf.urls import url
from vanilla import DetailView, TemplateView, View

from test.fixtures import WebTestCase
from db.views import TripsYearMixin


class TestView(TripsYearMixin, TemplateView):
    template_name = 'base.html'

urlpatterns = [
    url('^(?P<trips_year>[0-9]+)$', TestView.as_view(), name='test'),
]
    
@override_settings(ROOT_URLCONF='db.tests.test_trips_year')
class TripsYearMixinTests(WebTestCase):

    def test_dispatch_for_trips_year(self):
        year = self.init_current_trips_year()
        response = self.app.get('/' + str(year.year))
        self.assertEquals(response.status_code, 200)

    def test_dispatch_for_nonexistant_year(self):
        response = self.app.get('/2013', status=404)
        self.assertEquals(response.status_code, 404)



