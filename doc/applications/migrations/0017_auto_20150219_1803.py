# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0016_auto_20150219_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='assignment_preference',
            field=models.CharField(max_length=20, default='N/A', choices=[('PREFER_LEADER', 'Prefer Trip Leader'), ('PREFER_CROO', 'Prefer Croo'), ('N/A', 'N/A')], verbose_name="While Trips Directorate will ultimately decide where we think you will be most successful in the program, we would like to know your preferences. If you are submitting a Trip Leader application and a Croo application, please indicate which position you prefer. If you are only applying to one position, please choose 'N/A'"),
        ),
    ]
