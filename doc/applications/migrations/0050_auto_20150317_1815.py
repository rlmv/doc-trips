# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0049_auto_20150317_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='skippedcroograde',
            name='for_qualification',
            field=models.ForeignKey(editable=False, to='applications.QualificationTag', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='skippedcroograde',
            name='application',
            field=models.ForeignKey(related_name='skips', to='applications.CrooSupplement', editable=False),
        ),
        migrations.AlterField(
            model_name='skippedleadergrade',
            name='application',
            field=models.ForeignKey(related_name='skips', to='applications.LeaderSupplement', editable=False),
        ),
    ]
