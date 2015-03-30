# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0024_registration_firstchoice_triptype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='firstchoice_triptype',
            field=models.ForeignKey(blank=True, verbose_name='first choice trip types', related_name='firstchoice_triptype', to='trips.TripType', null=True),
        ),
    ]
