# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0028_auto_20150710_1737'),
    ]

    operations = [
        migrations.RenameField(
            model_name='triptemplate',
            old_name='description_conclusion',
            new_name='desc_conc',
        ),
        migrations.RenameField(
            model_name='triptemplate',
            old_name='description_day1',
            new_name='desc_day1',
        ),
        migrations.RenameField(
            model_name='triptemplate',
            old_name='description_day2',
            new_name='desc_day2',
        ),
        migrations.RenameField(
            model_name='triptemplate',
            old_name='description_day3',
            new_name='desc_day3',
        ),
        migrations.RenameField(
            model_name='triptemplate',
            old_name='description_introduction',
            new_name='desc_intro',
        ),
        migrations.RenameField(
            model_name='triptemplate',
            old_name='revision_notes',
            new_name='revisions',
        ),
    ]
