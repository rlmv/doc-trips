# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0002_auto_20150128_2042'),
        ('trips', '0003_auto_20150128_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='triptemplate',
            name='dropoff',
            field=models.ForeignKey(related_name='dropped_off_trips', to='transport.Stop', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='triptemplate',
            name='pickup',
            field=models.ForeignKey(related_name='picked_up_trips', to='transport.Stop', default=1),
            preserve_default=False,
        ),
    ]
