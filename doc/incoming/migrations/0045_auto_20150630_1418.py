# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def null_to_zero(apps, schema_editor):

    Registration = apps.get_model('incoming', 'Registration')
    for reg in Registration.objects.all():
        if reg.green_fund_donation is None:
            print('changing %s' % reg)
            reg.green_fund_donation = 0
            reg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0044_auto_20150629_1505'),
    ]

    operations = [
        migrations.RunPython(null_to_zero)
    ]
