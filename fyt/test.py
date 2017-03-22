import logging

from django.conf import settings
from django_webtest import WebTest
from model_mommy import mommy

from fyt.db.models import TripsYear
from fyt.permissions.permissions import (
    croo_heads,
    directorate,
    directors,
    graders,
    safety_leads,
    trip_leader_trainers,
)
from fyt.users.models import DartmouthUser


class FytTestCase(WebTest):
    """
    WebTest allows us to make requests without having to mock CAS
    authentication. See django_webtest for more details.

    For some reason whitenoise's GzipManifestStaticFilesStorage doesn't
    work with WebTest. We patch it here back to the django default storage.
    """

    def _patch_settings(self):
        super()._patch_settings()

        # Disable logging to console during testing.
        # Note that this disables all logging; if you need to test whether
        # something is being logged than you'll need to come up with a better
        # solution to this.
        logging.disable(logging.CRITICAL)

        self._STATICFILES_STORAGE = settings.STATICFILES_STORAGE
        settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

    def _unpatch_settings(self):
        super()._unpatch_settings()
        logging.disable(logging.NOTSET)
        settings.STATICFILES_STORAGE = self._STATICFILES_STORAGE

    def init_trips_year(self):
        """
        Initialize a current trips_year object in the test database.

        This should be called in the setUp() method of most TestCases,
        otherwise the database is going to barf when there is no current
        trips_year.
        """
        self.trips_year = mommy.make(TripsYear, year=2014, is_current=True)
        return self.trips_year

    def init_old_trips_year(self):
        self.old_trips_year = mommy.make(TripsYear, year=2013, is_current=False)
        return self.old_trips_year

    def make_user(self):
        """
        Create a user.
        """
        netid = 'user'
        email = netid + '@dartmouth.edu'
        self.user = DartmouthUser.objects.create_user(netid, netid, email)

        return self.user

    def make_incoming_student(self):
        netid = 'incoming'
        name = 'incoming'
        email = netid + '@dartmouth.edu'
        self.user = DartmouthUser.objects.create_user(netid, name, email)

        return self.user

    def make_director(self):
        """
        Create a user with director permissions, and log the user in.
        """
        netid = 'director'
        email = netid + '@dartmouth.edu'
        self.director = DartmouthUser.objects.create_user(netid, netid, email)
        self.director.groups.add(directors())
        self.director.save()

        return self.director

    def make_croo_head(self):
        netid = 'croo head'
        email = netid + '@dartmouth.edu'
        self.croo_head = DartmouthUser.objects.create_user(netid, netid, email)
        self.croo_head.groups.add(croo_heads())
        self.croo_head.save()

        return self.croo_head

    def make_directorate(self):
        """
        Create a user with directorate permissions, and log the user in.
        """
        netid = 'directorate'
        email = netid + '@dartmouth.edu'
        self.directorate = DartmouthUser.objects.create_user(netid, netid, email)
        self.directorate.groups.add(directorate())
        self.directorate.save()

        return self.directorate

    def make_tlt(self):
        """
        Create a user with trip leader trainer permissions, and log the user in.
        """
        netid = 'tlt'
        email = netid + '@dartmouth.edu'
        self.tlt = DartmouthUser.objects.create_user(netid, netid, email)
        self.tlt.groups.add(trip_leader_trainers())
        self.tlt.save()

        return self.tlt

    def make_grader(self):
        netid = 'grader'
        email = netid + '@dartmouth.edu'
        self.grader = DartmouthUser.objects.create_user(netid, netid, email)
        self.grader.groups.add(graders())
        self.grader.save()

        return self.grader

    def make_safety_lead(self):
        netid = 'safety'
        email = netid + '@dartmouth.edu'
        self.safety_lead = DartmouthUser.objects.create_user(netid, netid, email)
        self.safety_lead.groups.add(safety_leads())
        self.safety_lead.save()

        return self.safety_lead

    def assertQsEqual(self, qs, values, transform=lambda x: x, ordered=False, msg=None):
        """
        Override django assertQuerysetEqual with more useful arguments.
        """
        return self.assertQuerysetEqual(qs, values, transform=transform,
                                        ordered=ordered, msg=msg)
