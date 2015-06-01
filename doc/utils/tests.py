import unittest

from model_mommy import mommy

from doc.utils.matrix import OrderedMatrix
from doc.utils.fmt import section_range
from doc.trips.models import Section
from doc.test.fixtures import TripsYearTestCase


class MatrixFuncsTestCase(unittest.TestCase):

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
        self.assertTrue(m[0][0]==m[0][1]==m[1][0]==m[1][1]==1)

    def test_map_creates_new_instance(self):
        rows = [0, 1]
        cols = [0, 1]
        m = OrderedMatrix(rows, cols, default=0)
        n = m.map(lambda x: x + 1)
        self.assertEqual(m[0][0], 1)
        

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
