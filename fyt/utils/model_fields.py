
from django.db import models

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
