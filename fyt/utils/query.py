"""
Utils for querys and querysets.
"""

def pks(qs):
    """
    Return the primary keys of a queryset.
    """
    return qs.values_list('pk', flat=True)
