# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0017_auto_20150310_1431'),
        ('transport', '0021_auto_20150325_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledtransport',
            name='section',
            field=models.ForeignKey(to='trips.Section', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scheduledtransport',
            name='date',
            field=models.DateField(null=True),
        ),
    ]
