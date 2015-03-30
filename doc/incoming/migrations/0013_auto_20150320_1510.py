# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trippees', '0012_auto_20150314_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='cell_phone',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='guardian_email',
            field=models.EmailField(verbose_name='parent/guardian email', max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='home_phone',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='other_activities',
            field=models.TextField(verbose_name='Do you do any other activities that might assist us in assigning you to a trip (yoga, karate, horseback riding, photography, fishing, etc.)?', blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='physical_activities',
            field=models.TextField(verbose_name='Please describe the types of physical activities you enjoy, including frequency (daily? weekly?) and extent (number of miles or hours)', blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='regular_exercise',
            field=models.CharField(choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Do you do enjoy cardiovascular exercise (running, biking, swimming, sports, etc.) on a regular basis?', max_length=2),
        ),
        migrations.AlterField(
            model_name='registration',
            name='summer_plans',
            field=models.TextField(verbose_name='Please describe your plans for the summer (working at home, volunteering, etc.)', blank=True),
        ),
    ]
