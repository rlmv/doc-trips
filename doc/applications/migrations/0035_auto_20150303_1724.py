# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0034_auto_20150303_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crooapplicationgrade',
            name='potential_croos',
            field=models.ManyToManyField(verbose_name='I think this applicant is qualified for, and would do well on, the following Croos:', to='croos.Croo', blank=True),
        ),
    ]
