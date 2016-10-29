# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fyt.incoming.models


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0018_auto_20160725_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='section_choice',
        ),
        migrations.AddField(
            model_name='registration',
            name='section_choice',
            field=models.ManyToManyField(to='trips.Section',
                                         through='incoming.SectionChoice')
        ),
    ]
