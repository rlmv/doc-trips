# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raids', '0003_auto_20150728_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raid',
            name='plan',
            field=models.TextField(blank=True, help_text='Do you have a theme? Are you going to intercept the trip on the trail or at their campsite?'),
        ),
    ]
