from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone
from model_mommy import mommy

from fyt.test import FytTestCase
from fyt.timetable.models import Timetable


class TimetableTestCase(FytTestCase):

    def test_application_grace_period(self):
        now = timezone.now()
        timetable = mommy.make(Timetable)

        # With a 15-minute grace period, applications should still be available
        # 10 minutes past the deadline
        timetable.applications_open = now - timedelta(weeks=1)
        timetable.applications_close = now - timedelta(minutes=10)
        timetable.save()
        self.assertTrue(timetable.applications_available())

        # ... but not 20 minutes past
        timetable.applications_close = now - timedelta(minutes=20)
        timetable.save()
        self.assertFalse(timetable.applications_available())

    def test_applications_and_scoring_cannot_both_be_open(self):
        now = timezone.now()
        timetable = mommy.make(Timetable)

        timetable.applications_open = now - timedelta(weeks=1)
        timetable.applications_close = now + timedelta(minutes=10)
        timetable.scoring_available = True

        with self.assertRaises(ValidationError):
            timetable.full_clean()
