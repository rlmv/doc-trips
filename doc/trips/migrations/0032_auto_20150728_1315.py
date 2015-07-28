# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0031_trip_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='notes',
            field=models.TextField(blank=True, help_text='Trip-specific details such as weird timing. This information will be added to leader packets.'),
        ),
    ]
