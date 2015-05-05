import unittest

from doc.utils.matrix import make_ordered_matrix, truncate_matrix

class MatrixFuncsTestCase(unittest.TestCase):

    def test_truncate_matrix(self):
        rows = [0, 1]
        cols = [0, 1]
        m = make_ordered_matrix(rows, cols)
        m[0][0] = True
        self.assertEqual(truncate_matrix(m), {0: {0: True, 1: None}})


        
