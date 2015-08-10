from django.core.urlresolvers import reverse

from doc.test.testcases import WebTestCase


class IncidentViewsTestCase(WebTestCase):

    def test_safety_leads_can_access_incident_report(self):
        trips_year = self.init_trips_year()
        url = reverse('db:safety:list', kwargs={'trips_year': trips_year})
        self.app.get(url, user=self.mock_user(), status=403)
        self.app.get(url, user=self.mock_director())  # OK
        self.app.get(url, user=self.mock_safety_lead())  # OK
