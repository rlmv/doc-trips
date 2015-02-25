# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0015_auto_20150218_2259'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalapplication',
            name='assignment_preference',
            field=models.CharField(verbose_name="While Trips Directorate will ultimately decide where we think you will be most successful in the program, we would like to know your preferences. If you are applying for a Croo and for a Trip Leader, please indicate which position you prefer. If you are only applying to one position, please choose 'N/A'", default='N/A', max_length=20, choices=[('PREFER_LEADER', 'Prefer Trip Leader'), ('PREFER_CROO', 'Prefer Croo'), ('N/A', 'N/A')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='hanover_in_fall',
            field=models.CharField(verbose_name='Are you planning to be in Hanover this fall?', default=False, max_length=5, choices=[('YES', 'yes'), ('NO', 'no')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='croosupplement',
            name='assigned_croo',
            field=models.ForeignKey(blank=True, related_name='croolings', to='croos.Croo', null=True),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='personal_activities',
            field=models.TextField(blank=True, verbose_name='In order of importance to you, please list your activities and involvements at Dartmouth and beyond (e.g. greek affiliation, affinity group, campus organization, team, etc)'),
        ),
    ]
