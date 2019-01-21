import unittest

from django.template import Context, Template
from model_mommy import mommy

from fyt.core.templatetags.links import pass_null
from fyt.test import FytTestCase
from fyt.trips.models import Section


class NullPassThroughDecorator(unittest.TestCase):
    def test_decorator(self):
        @pass_null
        def add_one(x):
            return x + 1

        self.assertEqual(add_one(5), 6)
        self.assertEqual(add_one(False), False)


class LinkTagTestCase(FytTestCase):
    def test_detail_link(self):
        trips_year = self.init_trips_year()
        # for example
        obj = mommy.make(Section, trips_year=trips_year)
        obj.__str__ = lambda self: 'B'
        out = Template("{% load links %}" "{{ obj|detail_link }}").render(
            Context({'obj': obj})
        )

    def test_detail_link_null_input(self):
        out = Template("{% load links %}" "{{ obj|detail_link|default:'*' }}").render(
            Context({'obj': None})
        )
        self.assertEqual(out, '*')

    def test_detail_link_with_0_as_text(self):
        trips_year = self.init_trips_year()
        obj = mommy.make(Section, trips_year=trips_year)
        out = Template("{% load links %}" "{{ obj|detail_link:0 }}").render(
            Context({'obj': obj})
        )
        target = '<a href="%s">0</a>' % (obj.detail_url())
        self.assertEqual(out, target)

    def test_detail_link_with_unary_iterable(self):
        trips_year = self.init_trips_year()
        # for example
        obj = mommy.make(Section, trips_year=trips_year)
        out = Template("{% load links %}" "{{ obj_list|detail_link }}").render(
            Context({'obj_list': [obj]})
        )
        target = '<a href="%s">%s</a>' % (obj.detail_url(), str(obj))
        self.assertEqual(out, target)

    def test_detail_link_with_iterable(self):
        trips_year = self.init_trips_year()
        obj1 = mommy.make(Section, trips_year=trips_year)
        obj2 = mommy.make(Section, trips_year=trips_year)
        out = Template("{% load links %}" "{{ obj_list|detail_link }}").render(
            Context({'obj_list': [obj1, obj2]})
        )
        target = '<a href="{}">{}</a>, <a href="{}">{}</a>'.format(
            obj1.detail_url(), str(obj1), obj2.detail_url(), str(obj2)
        )
        self.assertEqual(out, target)

    def test_create_url(self):
        trips_year = self.init_trips_year()
        obj = mommy.make(Section, trips_year=trips_year)
        out = Template("{% load links %}" "{% create_url model trips_year %}").render(
            Context({'model': Section, 'trips_year': trips_year})
        )
        self.assertEqual(out, obj.create_url(trips_year))
