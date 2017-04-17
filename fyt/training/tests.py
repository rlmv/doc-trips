
from model_mommy import mommy

from fyt.test import FytTestCase
from fyt.training.models import Session, Attendee
from fyt.training.forms import AttendanceForm


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


class AttendenceFormTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.session = mommy.make(Session, trips_year=self.trips_year)
        self.attendee = mommy.make(Attendee, trips_year=self.trips_year,
                                   sessions=[self.session])
        self.not_attending = mommy.make(Attendee, trips_year=self.trips_year)

    def test_queryset_is_all_registered_volunteers(self):
        form = AttendanceForm(instance=self.session)
        self.assertQsEqual(form.fields['completed'].queryset, [self.attendee])

    def test_initial_is_populated(self):
        self.session.completed.add(self.attendee)
        form = AttendanceForm(instance=self.session)
        self.assertQsEqual(form.fields['completed'].initial, [self.attendee])

    def test_form_saves_attendance(self):
        self.assertQsEqual(self.session.completed.all(), [])
        form = AttendanceForm(
            {'completed': [self.attendee]},
            instance=self.session)
        form.save()
        self.session.refresh_from_db()
        self.assertQsEqual(self.session.completed.all(), [self.attendee])
