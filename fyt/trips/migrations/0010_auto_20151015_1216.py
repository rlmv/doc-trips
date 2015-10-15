# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def flip_swimtest(apps, schema_editor):
    """
    Populate the swimtest_required field as the opposite of the
    non_swimmers_allowed field.
    """
    TripTemplate = apps.get_model('trips', 'TripTemplate')
    for tt in TripTemplate.objects.all():
        tt.swimtest_required = not tt.non_swimmers_allowed
        tt.save()


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0009_triptemplate_swimtest_required'),
    ]

    operations = [
        migrations.RunPython(flip_swimtest)
    ]
