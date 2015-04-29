from collections import OrderedDict

def make_ordered_matrix(rows, cols, default=None):
    """
    Return a matrix with iterable rows and columns.

    default is a value or a callable
    """
    matrix = OrderedDict()
    for r in rows:
        matrix[r] = OrderedDict()
        for c in cols:
            if callable(default):
                matrix[r][c] = default()
            else:
                matrix[r][c] = default

    return matrix
