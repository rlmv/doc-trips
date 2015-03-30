# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0003_auto_20150310_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trippeeregistration',
            name='bus_stop',
            field=models.ForeignKey(to='transport.Stop', verbose_name='Where would you like to be bussed from/to?', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
