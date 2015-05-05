from collections import OrderedDict

""" 
TODO: make this object oriented: OrderedMatrix
"""

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


def truncate_matrix(matrix):
    """ 
    Remove all empty rows from matrix

    Returns <matrix> with all rows for which 
    matrix[row][col] evaluates to False for all cols 
    removed.
    """
    for row, cols in matrix.items():
        if not any(cols.values()):
            matrix.pop(row)
    return matrix
