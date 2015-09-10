from collections import OrderedDict


class OrderedMatrix(OrderedDict):
    """ 
    Holds a matrix of objects.
    
    Unlike a numerical matrix, the entries can be keyed 
    with any hashable object.
    """
    def __init__(self, rows, cols, default=None):
        super(OrderedMatrix, self).__init__()
        self.rows = rows
        self.cols = cols
        for r in rows:
            self[r] = OrderedDict()
            for c in cols:
                if callable(default):
                    self[r][c] = default()
                else:
                    self[r][c] = default
                    
    def truncate(self):
        """
        Remove all empty rows from matrix
        
        Returns <matrix> with all rows for which
        matrix[row][col] evaluates to False for all cols
        removed.
        """
        for row, cols in self.items():
            if not any(cols.values()):
                self.pop(row)
        return self

    def map(self, func):
        """
        Perform a mapping over the matrix.
        
        Returns a new OrderedMatrix with each entry set as
        new[row][col] = func(orig[row][col])
        """
        new = OrderedMatrix(self.rows, self.cols)
        for row in self.rows:
            for col in self.cols:
                new[row][col] = func(self[row][col])
        return new
