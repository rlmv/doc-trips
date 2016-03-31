
from django.core.exceptions import ValidationError
from django.test import TestCase

from fyt.dartdm.forms import DartmouthDirectoryLookupField


class DartmouthDirectoryLookupFieldTestCase(TestCase):

    def test_compress(self):
        field = DartmouthDirectoryLookupField()

        # Ambiguous name
        with self.assertRaises(ValidationError):
            field.compress(['Robert L. Marchman'])

        # Not found
        with self.assertRaises(ValidationError):
            field.compress(['Robert L. Marchmanxyzsgasdgasdf'])

        answer = {
            'netid': 'd34898x',
            'name_with_affil': 'Robert L. Marchman 14 (Alum/14)',
            'name_with_year': 'Robert L. Marchman 14'
        }

        # Entered before typeahead completed
        self.assertEqual(field.compress(['Robert L. Marchman 14']), answer)

        # Entered after typeahead completed
        data_list = ['Robert L. Marchman 14', 'd34898x',
                     'Robert L. Marchman 14 (Alum/14)']
        self.assertEqual(field.compress(data_list), answer)
