
from django.db import models

"""
Testing migrations:
https://gist.github.com/blueyed/4fb0a807104551f103e6
"""

YES_NO_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
)


def YesNoField(*args, **kwargs):
    kwargs['choices'] = YES_NO_CHOICES
    kwargs['default'] = False
    return models.BooleanField(*args, **kwargs)


def NullYesNoField(*args, **kwargs):
    kwargs['choices'] = YES_NO_CHOICES
    kwargs['default'] = None
    return models.NullBooleanField(*args, **kwargs)
