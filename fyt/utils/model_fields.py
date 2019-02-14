from django.db import models


YES_NO_CHOICES = ((True, 'Yes'), (False, 'No'))
YES_NO_NONE_CHOICES = ((None, '----'), (True, 'Yes'), (False, 'No'))


def YesNoField(*args, **kwargs):
    kwargs['choices'] = YES_NO_CHOICES
    kwargs['default'] = False
    return models.BooleanField(*args, **kwargs)


def NullYesNoField(*args, **kwargs):
    kwargs['choices'] = YES_NO_NONE_CHOICES
    kwargs['default'] = None
    kwargs['null'] = True
    kwargs['blank'] = True
    return models.BooleanField(*args, **kwargs)
