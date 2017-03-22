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

    def make_person(self, name, *groups):
        """
        Create a user in the given groups.
        """
        netid = name
        email = name + '@dartmouth.edu'

        user = DartmouthUser.objects.create_user(netid, name, email)
        user.groups.add(*groups)

        return user

    def make_user(self):
        """
        Create a user.
        """
        self.user = self.make_person('user')
        return self.user

    def make_incoming_student(self):
        """
        Create an incoming student.
        """
        self.incoming = self.make_person('incoming')
        return self.incoming

    def make_director(self):
        """
        Create a user with director permissions.
        """
        self.director = self.make_person('director', directors())
        return self.director

    def make_croo_head(self):
        """
        Create a user with croo head permissions.
        """
        self.croo_head = self.make_person('croo head', croo_heads())
        return self.croo_head

    def make_directorate(self):
        """
        Create a user with directorate permissions.
        """
        self.directorate = self.make_person('directorate', directorate())
        return self.directorate

    def make_tlt(self):
        """
        Create a user with TLT permissions.
        """
        self.tlt = self.make_person('tlt', trip_leader_trainers())
        return self.tlt

    def make_grader(self):
        """
        Create a user with grader permissions.
        """
        self.grader = self.make_person('grader', graders())
        return self.grader

    def make_safety_lead(self):
        """
        Create a user with grader permissions.
        """
        self.safety_lead = self.make_person('safety', safety_leads())
        return self.safety_lead

    def assertQsEqual(self, qs, values, transform=lambda x: x, ordered=False, msg=None):
        """
        Override django assertQuerysetEqual with more useful arguments.
        """
        return self.assertQuerysetEqual(qs, values, transform=transform,
                                        ordered=ordered, msg=msg)
