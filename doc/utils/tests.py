import unittest

from model_mommy import mommy

from doc.utils.matrix import make_ordered_matrix, truncate_matrix
from doc.utils.fmt import section_range
from doc.trips.models import Section
from doc.test.fixtures import TripsYearTestCase


class MatrixFuncsTestCase(unittest.TestCase):

    def test_truncate_matrix(self):
        rows = [0, 1]
        cols = [0, 1]
        m = make_ordered_matrix(rows, cols)
        m[0][0] = True
        self.assertEqual(truncate_matrix(m), {0: {0: True, 1: None}})


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
