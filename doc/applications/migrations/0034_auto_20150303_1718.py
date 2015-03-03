# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0009_auto_20150220_1800'),
        ('applications', '0033_auto_20150303_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='potential_croos',
            field=models.ManyToManyField(to='croos.Croo', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='kitchen_lead',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='kitchen_lead_qualified',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
