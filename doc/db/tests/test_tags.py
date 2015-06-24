import unittest

from django.template import Context, Template
from model_mommy import mommy

from doc.test.fixtures import TripsTestCase
from doc.trips.models import Section
from doc.db.templatetags.links import pass_null

class NullPassThroughDecorator(unittest.TestCase):

    def test_decorator(self):
        @pass_null
        def add_one(x):
            return x + 1
        self.assertEqual(add_one(5), 6)
        self.assertEqual(add_one(False), False)


class LinkTagTestCase(TripsTestCase):
    
    def test_detail_link(self):
        trips_year = self.init_trips_year()
        # for example
        obj = mommy.make(Section, trips_year=trips_year)
        obj.__str__ = lambda self: 'B'
        out = Template(
            "{% load links %}"
            "{{ obj|detail_link }}"
        ).render(Context({
            'obj': obj
        }))


    def test_detail_link_null_input(self):
        trips_year = self.init_trips_year()
        # for example
        out = Template(
            "{% load links %}"
            "{{ obj|detail_link|default:'*' }}"
        ).render(Context({
            'obj': None
        }))
        self.assertEqual(out, '*')
        
            
        
