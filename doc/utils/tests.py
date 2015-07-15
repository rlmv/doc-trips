import unittest

from model_mommy import mommy

from doc.utils.matrix import OrderedMatrix
from doc.utils.fmt import section_range
from doc.trips.models import Section
from doc.test.testcases import TripsYearTestCase
from doc.utils.lat_lng import parse_lat_lng


class OrderedMatrixTestCase(unittest.TestCase):

    def test_truncate_matrix(self):
        rows = [0, 1]
        cols = [0, 1]
        m = OrderedMatrix(rows, cols)
        m[0][0] = True
        self.assertEqual(m.truncate(), {0: {0: True, 1: None}})

    def test_map(self):
        rows = [0, 1]
        cols = [0, 1]
        m = OrderedMatrix(rows, cols, default=0)
        n = m.map(lambda x: x + 1)
        self.assertTrue(n[0][0]==n[0][1]==n[1][0]==n[1][1]==1)

    def test_map_creates_new_instance(self):
        rows = [0, 1]
        cols = [0, 1]
        m = OrderedMatrix(rows, cols, default=0)
        n = m.map(lambda x: x + 1)
        self.assertEqual(m[0][0], 0)
        

class FmtUtilsTest(TripsYearTestCase):

    def test_section_range(self):
        mommy.make(Section, name="A")
        mommy.make(Section, name="B")
        mommy.make(Section, name="C")
        self.assertEqual(section_range(Section.objects.all()), "A - C")

    def test_section_range_not_contiguous(self):
        mommy.make(Section, name="A")
        mommy.make(Section, name="C")
        with self.assertRaises(AssertionError):
            section_range(Section.objects.all())


class LatLngRegex(unittest.TestCase):

    def test_lat_lng(self):
        tests = [
            ('13.0,153.5', '13.0,153.5'),
            ('23.0, 153.5', '23.0,153.5'),
            ('33.0,153.5', '33.0,153.5'),
            ('-43.0, -153.5', '-43.0,-153.5'),
            ("""44° 2'39.67"N 71°47'31.72"W""", None)  # no match
            # ...
        ]
        for string, target in tests:
            self.assertEqual(target, parse_lat_lng(string))
