# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0040_scheduledtransport_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledtransport',
            name='notes',
            field=models.TextField(help_text='for the bus driver'),
        ),
    ]
