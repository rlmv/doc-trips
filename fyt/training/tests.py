
from django.core.urlresolvers import reverse
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
            registered_sessions=[self.session],
            volunteer__applicant__email='test@gmail.com')

    def test_attendee_emails(self):
        self.assertQsEqual(self.session.registered_emails(), ['test@gmail.com'])


class AttendenceFormTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.session = mommy.make(Session, trips_year=self.trips_year)
        self.attendee = mommy.make(Attendee, trips_year=self.trips_year,
                                   registered_sessions=[self.session])
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


class TrainingViewsTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.make_user()
        self.make_director()
        self.make_directorate()
        self.make_croo_head()
        self.make_tlt()
        self.make_safety_lead()

    def test_db_views_permissions(self):
        session = mommy.make(Session, trips_year=self.trips_year)
        update_urls = [
            session.update_url(),
            session.delete_url(),
            Session.create_url(self.trips_year),
        ]
        for url in update_urls:
            self.app.get(url, user=self.tlt)
            self.app.get(url, user=self.director)
            self.app.get(url, user=self.directorate, status=403)
            self.app.get(url, user=self.user, status=403)
            self.app.get(url, user=self.croo_head, status=403)
            self.app.get(url, user=self.safety_lead, status=403)

        # Directorate members can also update attendance
        url = reverse('db:session:update_attendance', kwargs=session.obj_kwargs())
        self.app.get(url, user=self.tlt)
        self.app.get(url, user=self.director)
        self.app.get(url, user=self.directorate)
        self.app.get(url, user=self.user, status=403)
        self.app.get(url, user=self.croo_head, status=403)
        self.app.get(url, user=self.safety_lead, status=403)
