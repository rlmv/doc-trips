# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0039_auto_20150731_0958'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledtransport',
            name='notes',
            field=models.TextField(default='', help_text='notes to the bus driver'),
            preserve_default=False,
        ),
    ]
