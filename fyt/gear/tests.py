from django.core.exceptions import ValidationError
from model_mommy import mommy

from .models import GearRequest

from fyt.test import FytTestCase


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
