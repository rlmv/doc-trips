from django.core.urlresolvers import reverse
from model_mommy import mommy

from fyt.applications.models import Volunteer
from fyt.applications.tests import ApplicationTestMixin
from fyt.test import FytTestCase
from fyt.training.forms import AttendanceForm, AttendeeUpdateForm, FirstAidFormset, SignupForm, SessionRegistrationForm
from fyt.training.models import Attendee, Session, Training


# Don't let model_mommy bung up the OneToOne creation
def make_attendee(trips_year=None, **kwargs):
    volunteer = mommy.make(Volunteer, trips_year=trips_year,
                           applicant__email='test@gmail.com')
    for k, v in kwargs.items():
        setattr(volunteer.attendee, k, v)
    volunteer.attendee.save()
    return volunteer.attendee


class SessionModelTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.session = mommy.make(Session, trips_year=self.trips_year)
        self.attendee = make_attendee(
            trips_year=self.trips_year,
            registered_sessions=[self.session])

    def test_attendee_emails(self):
        self.assertQsEqual(self.session.registered_emails(), ['test@gmail.com'])

    def test_full(self):
        self.assertFalse(self.session.full())
        for i in range(Session.DEFAULT_CAPACITY):
            make_attendee(trips_year=self.trips_year,
                          registered_sessions=[self.session])
        self.assertTrue(self.session.full())


class AttendeeModelTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()

    def test_attendee_is_created_for_each_volunteer(self):
        volunteer = mommy.make(Volunteer, trips_year=self.trips_year)
        attendee = volunteer.attendee
        self.assertEqual(attendee.trips_year, self.trips_year)

    def test_training_complete(self):
        attendee = make_attendee(trips_year=self.trips_year)
        self.assertTrue(attendee.training_complete())
        self.assertEqual(attendee.trainings_to_sessions(), {})

        # One unattended training
        training = mommy.make(Training, trips_year=self.trips_year)
        self.assertFalse(attendee.training_complete())
        self.assertEqual(attendee.trainings_to_sessions(), {
            training: None})

        # Go to a session
        session = mommy.make(Session, trips_year=self.trips_year,
                             training=training, completed=[attendee])
        attendee = Attendee.objects.get(pk=attendee.pk)
        self.assertTrue(attendee.training_complete())
        self.assertEqual(attendee.trainings_to_sessions(), {
            training: session})

    def test_get_first_aid_cert(self):
        attendee = make_attendee(trips_year=self.trips_year, fa_cert='WFR')
        self.assertEqual(attendee.get_first_aid_cert(), 'WFR')

    def test_get_first_aid_cert_other(self):
        attendee = make_attendee(
            trips_year=self.trips_year,
            fa_cert=Attendee.OTHER,
            fa_other='ABC')
        self.assertEqual(attendee.get_first_aid_cert(), 'ABC')

    def test_get_first_aid_cert_without_explicit_other(self):
        attendee = make_attendee(
            trips_year=self.trips_year,
            fa_cert="",
            fa_other='ABC')
        self.assertEqual(attendee.get_first_aid_cert(), 'ABC')

    def test_can_train(self):
        results = {
            Volunteer.CROO: True,
            Volunteer.LEADER: True,
            Volunteer.LEADER_WAITLIST: True,
            Volunteer.PENDING: False,
            Volunteer.PENDING: False,
            Volunteer.CANCELED: False,
            Volunteer.REJECTED: False
        }
        trainable = []
        for status, allowed in results.items():
            a = self.make_application(status=status).attendee
            self.assertEqual(a.can_register, allowed)
            if allowed:
                trainable.append(a)

        self.assertQsEqual(Attendee.objects.trainable(self.trips_year), trainable)


class SessionRegistrationFormTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.session = mommy.make(Session, trips_year=self.trips_year)
        self.attendee = self.make_application(status=Volunteer.LEADER).attendee
        self.make_application(status=Volunteer.REJECTED)

    def test_queryset_is_all_trainable_volunteers(self):
        form = SessionRegistrationForm(instance=self.session)
        self.assertQsEqual(form.fields['registered'].queryset, [self.attendee])

    def test_initial_is_populated(self):
        self.session.registered.add(self.attendee)
        form = SessionRegistrationForm(instance=self.session)
        self.assertQsEqual(form.fields['registered'].initial, [self.attendee])

    def test_form_saves_registration(self):
        form = SessionRegistrationForm({'registered': [self.attendee]},
                                       instance=self.session)
        form.save()
        self.session.refresh_from_db()
        self.assertQsEqual(self.session.registered.all(), [self.attendee])

    def test_form_removes_registrations(self):
        self.session.registered.add(self.attendee)
        form = SessionRegistrationForm({'registered': []},
                                       instance=self.session)
        form.save()
        self.session.refresh_from_db()
        self.assertQsEqual(self.session.registered.all(), [])


class AttendenceFormTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.session = mommy.make(Session, trips_year=self.trips_year)
        self.attendee = make_attendee(trips_year=self.trips_year,
                                      registered_sessions=[self.session])
        self.not_attending = make_attendee(trips_year=self.trips_year)

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

    def test_form_removes_attendance(self):
        self.session.completed.add(self.attendee)
        form = AttendanceForm({'completed': []}, instance=self.session)
        form.save()
        self.session.refresh_from_db()
        self.assertQsEqual(self.session.completed.all(), [])


class AttendeeUpdateFormTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.init_old_trips_year()

    def test_complete_sessions_queryset(self):
        session = mommy.make(Session, trips_year=self.trips_year)
        old_session = mommy.make(Session, trips_year=self.old_trips_year)
        attendee = make_attendee(trips_year=self.trips_year)
        form = AttendeeUpdateForm(instance=attendee)
        self.assertQsEqual(form.fields['complete_sessions'].queryset, [session])


class SignupFormTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()

    def test_session_size_is_capped(self):
        session = mommy.make(Session, trips_year=self.trips_year)
        for i in range(Session.DEFAULT_CAPACITY):
            make_attendee(trips_year=self.trips_year,
                          registered_sessions=[session])

        attendee = make_attendee(trips_year=self.trips_year)
        form = SignupForm({'registered_sessions': [session]}, instance=attendee)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'registered_sessions': [
                "The following sessions are full: {}. Please choose another "
                "session. If this is the only time you can attend, please "
                "contact the Trip Leader Trainers directly.".format(
                    session)]
        })

    def test_dont_check_capacity_when_previously_registered(self):
        session = mommy.make(Session, trips_year=self.trips_year)
        attendee = make_attendee(trips_year=self.trips_year,
                                 registered_sessions=[session])

        # Then session fills up
        for i in range(Session.DEFAULT_CAPACITY):
            make_attendee(trips_year=self.trips_year,
                          registered_sessions=[session])

        form = SignupForm({'registered_sessions': [session]}, instance=attendee)
        self.assertTrue(form.is_valid())
        self.assertQsEqual(form.cleaned_data['registered_sessions'], [session])


class FirstAidFormsetTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.leader = self.make_application(status=Volunteer.LEADER)
        self.crooling = self.make_application(status=Volunteer.CROO)
        self.leader_waitlist = self.make_application(
            status=Volunteer.LEADER_WAITLIST)
        self.pending = self.make_application(status=Volunteer.PENDING)

    def test_queryset(self):
        formset = FirstAidFormset(self.trips_year)
        self.assertQsEqual(formset.queryset,
            [self.leader.attendee,
             self.crooling.attendee,
             self.leader_waitlist.attendee])


class TrainingViewsTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.make_user()
        self.make_director()
        self.make_directorate()
        self.make_croo_head()
        self.make_tlt()
        self.make_safety_lead()

    def test_db_view_permissions(self):
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

    def test_external_view_permissions(self):
        results = {
            Volunteer.CROO: 200,
            Volunteer.LEADER: 200,
            Volunteer.LEADER_WAITLIST: 200,
            Volunteer.PENDING: 403,
            Volunteer.PENDING: 403,
            Volunteer.CANCELED: 403,
            Volunteer.REJECTED: 403
        }

        url = reverse('training:signup')
        for status, code in results.items():
            app = mommy.make(Volunteer, trips_year=self.trips_year, status=status)
            self.app.get(url, user=app.applicant, status=code)

    def test_num_queries(self):
        self.make_application(status=Volunteer.LEADER)
        url = reverse('db:attendee:first_aid', kwargs={
            'trips_year': self.trips_year})

        with self.assertNumQueries(15):
            self.app.get(url, user=self.director)
