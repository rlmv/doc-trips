# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0047_auto_20150713_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingstudent',
            name='hide_med_info',
            field=models.BooleanField(default=False, help_text='If selected, only the Med Info field of the Incoming Student will be exported to leader and croo packets.', verbose_name='Hide med info?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='med_info',
            field=models.TextField(blank=True, default='', help_text='Medical information additional to that provided in the registration.'),
            preserve_default=False,
        ),
    ]
