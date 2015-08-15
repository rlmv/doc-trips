
from django.db import models

"""
Testing migrations:
https://gist.github.com/blueyed/4fb0a807104551f103e6
"""

def YesNoField(*args, **kwargs):
    kwargs['choices'] = (
        (True, 'Yes'), (False, 'No')
    )
    kwargs['default'] = False
    return models.BooleanField(*args, **kwargs)


def NullYesNoField(*args, **kwargs):
    kwargs['choices'] = (
        (True, 'Yes'), (False, 'No')
    )
    kwargs['default'] = None
    return models.NullBooleanField(*args, **kwargs)
