# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0030_rename_ScheduledTrip_to_Trip'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='notes',
            field=models.TextField(blank=True, help_text='trip-specific details such as weird timing', default=''),
            preserve_default=False,
        ),
    ]
