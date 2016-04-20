
from datetime import timedelta

from django.utils import timezone

from fyt.timetable.models import Timetable
from fyt.test.testcases import TripsTestCase


class TimetableTestCase(TripsTestCase):

    def test_application_grace_period(self):
        now = timezone.now()
        timetable = Timetable.objects.timetable()

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
