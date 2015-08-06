# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0048_auto_20150806_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='hide_med_info',
            field=models.BooleanField(default=False, verbose_name='Hide registration med info?', help_text="Medical information in this trippee's registration will NOT be exported to leader and croo packets."),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='med_info',
            field=models.TextField(blank=True, help_text='Additional medical info not provided in the registration, or simplified information if some details do not need to be provided to leaders and croos.'),
        ),
    ]
