import re
from django.core.exceptions import ValidationError
from django.urls import reverse
from model_mommy import mommy

from .forms import GearRequestForm
from .models import Gear, GearRequest

from fyt.applications.models import Volunteer
from fyt.applications.tests import ApplicationTestMixin
from fyt.incoming.models import IncomingStudent, Settings
from fyt.test import FytTestCase
from fyt.timetable.models import Timetable
from fyt.users.models import DartmouthUser


class GearRequestModelTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()

    def test_validate_volunteer_or_incoming(self):
        # Neither incoming or volunteer
        with self.assertRaises(ValidationError):
            mommy.make(GearRequest).full_clean()

        # Can't be both incoming and volunteer
        with self.assertRaises(ValidationError):
            mommy.make(
                GearRequest,
                incoming_student__trips_year=self.trips_year,
                volunteer__trips_year=self.trips_year
            ).full_clean()

    def test_incoming_student_requester(self):
        gear_request = mommy.make(
            GearRequest,
            incoming_student__trips_year=self.trips_year)
        self.assertEqual(gear_request.incoming_student, gear_request.requester)
        self.assertEqual(gear_request.role, 'TRIPPEE')

    def test_volunteer_requester(self):
        gear_request = mommy.make(
            GearRequest,
            volunteer__trips_year=self.trips_year,
            volunteer__status=Volunteer.LEADER_WAITLIST)
        self.assertEqual(gear_request.volunteer, gear_request.requester)
        self.assertEqual(gear_request.role, 'LEADER_WAITLIST')


class GearRequestFormTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()

    def test_sets_requester(self):
        incoming = mommy.make(IncomingStudent, trips_year=self.trips_year)
        user = mommy.make(DartmouthUser, netid=incoming.netid)
        form = GearRequestForm(user=user,
                               data={'gear': [], 'additional': ''},
                               trips_year=self.trips_year)
        instance = form.save()
        self.assertEqual(instance.requester, incoming)


class GearRequestMatrixTestCase(FytTestCase):

    def setUp(self):
        self.init_trips_year()

    def test_matrix(self):
        gear1 = mommy.make(Gear, trips_year=self.trips_year)
        gear2 = mommy.make(Gear, trips_year=self.trips_year)
        request1 = mommy.make(GearRequest, trips_year=self.trips_year,
                              incoming_student__trips_year=self.trips_year)
        request1.gear.set([gear1])
        request2 = mommy.make(GearRequest, trips_year=self.trips_year,
                              volunteer__trips_year=self.trips_year)
        request2.gear.set([gear2])

        with self.assertNumQueries(3):
            matrix = GearRequest.objects.matrix(self.trips_year)
        self.assertEqual(matrix, {
            request1: {gear1: True, gear2: False},
            request2: {gear1: False, gear2: True}
        })


class GearRequestViewsTestCase(ApplicationTestMixin, FytTestCase):

    def setUp(self):
        self.init_trips_year()
        self.incoming_student_gear_request = mommy.make(
            GearRequest,
            trips_year=self.trips_year,
            incoming_student__trips_year=self.trips_year)
        self.volunteer_gear_request = mommy.make(
            GearRequest,
            trips_year=self.trips_year,
            volunteer=self.make_application())
        mommy.make(Settings, trips_year=self.trips_year)
        mommy.make(Timetable)

    def test_update_request_redirects_to_proper_view(self):
        urls = [
            reverse('core:gearrequest:list',
                    kwargs={'trips_year': self.trips_year}),
            self.incoming_student_gear_request.incoming_student.detail_url(),
            self.volunteer_gear_request.volunteer.detail_url()]

        director = self.make_director()
        update_url_regex = re.compile(r'gear-requests/\d+/update')
        for url in urls:
            resp1 = self.app.get(url, user=director)
            resp2 = resp1.click(href=update_url_regex, index=0)
            resp3 = resp2.form.submit()
            self.assertRedirects(resp3, url)
