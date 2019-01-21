import inspect
import itertools
import logging
import os
import string

from django.conf import settings
from django_webtest import WebTest
from model_mommy import mommy, random_gen
from vcr import VCR

from fyt.core.models import TripsYear
from fyt.permissions.permissions import groups
from fyt.users.models import DartmouthUser


# Model Mommy generates fake model data
# -----------------------------------------------------------------


def gen_class_year():
    return 2016


def gen_short_string(max_length):
    return random_gen.gen_string(min(max_length, 10))


gen_short_string.required = ['max_length']


mommy.generators.add('fyt.applications.models.ClassYearField', gen_class_year)
mommy.generators.add('fyt.users.models.NetIdField', random_gen.gen_string)
mommy.generators.add('django.db.models.CharField', gen_short_string)


# Use VCRpy to mock remote APIs
# -----------------------------------------------------------------


def path_generator(function):
    return os.path.join(
        os.path.dirname(inspect.getfile(function)), 'cassettes', function.__name__
    )


vcr = VCR(
    path_transformer=VCR.ensure_suffix('.yaml'),
    func_path_generator=path_generator,
    filter_query_parameters=['key'],
)  # Strip Google Maps API key


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

    def _unpatch_settings(self):
        super()._unpatch_settings()
        logging.disable(logging.NOTSET)

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
        self.director = self.make_person('director', groups.directors)
        return self.director

    def make_croo_head(self):
        """
        Create a user with croo head permissions.
        """
        self.croo_head = self.make_person('croo head', groups.croo_heads)
        return self.croo_head

    def make_directorate(self):
        """
        Create a user with directorate permissions.
        """
        self.directorate = self.make_person('directorate', groups.directorate)
        return self.directorate

    def make_tlt(self):
        """
        Create a user with TLT permissions.
        """
        self.tlt = self.make_person('tlt', groups.trip_leader_trainers)
        return self.tlt

    def make_grader(self):
        """
        Create a user with grader permissions.
        """
        self.grader = self.make_person('grader', groups.graders)
        return self.grader

    def make_safety_lead(self):
        """
        Create a user with grader permissions.
        """
        self.safety_lead = self.make_person('safety', groups.safety_leads)
        return self.safety_lead

    def assertQsEqual(self, qs, values, transform=lambda x: x, ordered=False, msg=None):
        """
        Override django assertQuerysetEqual with more useful arguments.
        """
        return self.assertQuerysetEqual(
            qs, values, transform=transform, ordered=ordered, msg=msg
        )

    def assertQsContains(self, qs, values, msg=None):
        """
        Compare a queryset to a list of dictionaries.

        The queryset and the list are considered equal if each object in the
        queryset contains all the values in the corresponding dict.

        The queryset is always considered to by ordered.
        """
        transformed = []

        for qs_obj, values_dict in itertools.zip_longest(qs, values):
            if values_dict is None:
                new = qs_obj
            elif qs_obj is None:
                break
            else:
                new = {key: getattr(qs_obj, key) for key in values_dict}
            transformed.append(new)

        return self.assertEqual(transformed, values)
