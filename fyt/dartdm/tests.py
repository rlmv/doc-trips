import os
import unittest

from django.core.exceptions import ValidationError

from fyt.dartdm.forms import DartmouthDirectoryLookupField
from fyt.dartdm.lookup import dartdm_lookup
from fyt.test import FytTestCase, vcr


class DartmouthDirectoryLookupFieldTestCase(FytTestCase):

    @vcr.use_cassette
    def test_compress(self):
        field = DartmouthDirectoryLookupField()

        # Ambiguous name
        with self.assertRaises(ValidationError):
            field.compress(['Robert L. Marchman'])

        # Not found
        with self.assertRaises(ValidationError):
            field.compress(['Robert L. Marchmanxyzsgasdgasdf'])

        answer = {
            'netid': 'a002bxd',
            'name_with_affil': 'Robert L. Marchman IV (Alum/76)',
            'name_with_year': 'Robert L. Marchman IV'
        }

        # Entered before typeahead completed
        self.assertEqual(field.compress(['Robert L. Marchman IV']), answer)

        # Entered after typeahead completed
        data_list = ['Robert L. Marchman IV', 'a002bxd',
                     'Robert L. Marchman IV (Alum/76)']
        self.assertEqual(field.compress(data_list), answer)


class DartdmLookupTestCase(unittest.TestCase):

    def test_too_short_query(self):
        self.assertEqual([], dartdm_lookup('A'))
