import logging
import os
import unittest

import requests
from django.core.exceptions import ValidationError

from fyt.dartdm.forms import DartmouthDirectoryLookupField
from fyt.dartdm.lookup import EmailLookupException, lookup_dartdm, lookup_email
from fyt.test import FytTestCase, vcr


class DartdmLookupFieldTestCase(FytTestCase):

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
            'name': 'Robert L. Marchman IV'
        }

        # Entered before typeahead completed
        self.assertEqual(field.compress(['Robert L. Marchman IV']), answer)

        # Entered after typeahead completed
        data_list = ['Robert L. Marchman IV', 'a002bxd',
                     'Robert L. Marchman IV']
        self.assertEqual(field.compress(data_list), answer)


class DartdmLookupTestCase(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_too_short_query(self):
        self.assertEqual([], lookup_dartdm('A'))

    @vcr.use_cassette
    def test_query_with_comma(self):
        self.assertEqual([], lookup_dartdm('a,'))


class EmailLookupTestCase(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @unittest.mock.patch('requests.get', side_effect=requests.ConnectionError)
    def test_connection_error(self, patched_get):
        with self.assertRaises(EmailLookupException):
            lookup_email('d348dgx')
