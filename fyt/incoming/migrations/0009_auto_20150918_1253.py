# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0008_auto_20150917_2107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='cancelled_fee',
            field=models.PositiveSmallIntegerField(verbose_name='cancellation fee', blank=True, help_text="Customize the cancellation fee. Otherwise a 'cancelled' student is by default charged the full cost of trips (adjusted by financial aid, if applicable). ", null=True),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='med_info',
            field=models.TextField(verbose_name='additional med info', blank=True, help_text='Use this field for additional medical info not provided in the registration, or simplified information if some details do not need to be provided to leaders and croos. This is always exported to leader packets.'),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='show_med_info',
            field=models.BooleanField(verbose_name='Show registration med info?', default=False, help_text="Medical information in this trippee's registration will be displayed in leader and croo packets."),
        ),
    ]
