from django.core.exceptions import ValidationError
from model_mommy import mommy

from .forms import GearRequestForm
from .models import GearRequest

from fyt.incoming.models import IncomingStudent
from fyt.test import FytTestCase
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

    def test_volunteer_requester(self):
        gear_request = mommy.make(
            GearRequest,
            volunteer__trips_year=self.trips_year)
        self.assertEqual(gear_request.volunteer, gear_request.requester)


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
