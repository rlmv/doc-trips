
from model_mommy import mommy

from fyt.test import FytTestCase
from fyt.training.models import Session, Attendee


class SessionModelTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.session = mommy.make(Session, trips_year=self.trips_year)
        self.attendee = mommy.make(
            Attendee,
            trips_year=self.trips_year,
            sessions=[self.session],
            volunteer__applicant__email='test@gmail.com')

    def test_attendee_emails(self):
        self.assertQsEqual(self.session.attendee_emails(), ['test@gmail.com'])
