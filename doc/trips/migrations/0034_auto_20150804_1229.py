# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0033_auto_20150804_1117'),
    ]

    operations = [
        migrations.RenameField(
            model_name='triptemplate',
            old_name='dropoff',
            new_name='dropoff_stop',
        ),
        migrations.RenameField(
            model_name='triptemplate',
            old_name='pickup',
            new_name='pickup_stop',
        ),
    ]
