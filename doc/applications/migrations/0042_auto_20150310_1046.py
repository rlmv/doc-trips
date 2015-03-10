# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0041_auto_20150310_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qualificationtag',
            name='name',
            field=models.CharField(max_length=30, verbose_name='I think this applicant is qualified for the following roles:'),
        ),
    ]
