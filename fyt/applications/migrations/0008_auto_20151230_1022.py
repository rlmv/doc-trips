# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def use_boolean_yes_no_fields(apps, schema_editor):
    """Convert CharFields with 'YES', 'NO', values to BooleanFields"""
    GeneralApplication = apps.get_model('applications', 'GeneralApplication')

    mapping = {
        'YES': True,
        'NO': False,
    }

    for app in GeneralApplication.objects.all():
        app._hanover_in_fall = mapping[app.hanover_in_fall]
        app.save()


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0007_generalapplication__hanover_in_fall'),
    ]

    operations = [
        migrations.RunPython(use_boolean_yes_no_fields)
    ]
