# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0020_auto_20140915_2207'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sectionpreferences',
            name='leader',
        ),
        migrations.RemoveField(
            model_name='sectionpreferences',
            name='section',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='through_sections',
        ),
        migrations.DeleteModel(
            name='SectionPreferences',
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='status',
            field=models.CharField(default='PEND', max_length=4, choices=[('PEND', 'Pending'), ('ACC', 'Accepted'), ('WAIT', 'Waitlisted'), ('REJ', 'Rejected'), ('CROO', 'Croo'), ('CANC', 'Cancelled'), ('DEP', 'Deprecated'), ('DISQ', 'Disqualified')], verbose_name='Application status'),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='user',
            field=models.ForeignKey(verbose_name='Applicant', to=settings.AUTH_USER_MODEL),
        ),
    ]
