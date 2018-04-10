"""
Utils for queries and querysets.
"""

from django.db import models


def pks(qs):
    """
    Return the primary keys of a queryset.
    """
    return qs.values_list('pk', flat=True)


def TrueIf(**kwargs):
    """
    Return a case expression that evaluates to True if the query conditions
    are met, else False
    """
    return models.Case(
        models.When(then=True, **kwargs),
        default=False,
        output_field=models.BooleanField()
    )
