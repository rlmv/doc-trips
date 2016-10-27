# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0022_auto_20161026_1534'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registration',
            old_name='available_sections',
            new_name='_old_available_sections',
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='available_triptypes',
            new_name='_old_available_triptypes',
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='firstchoice_triptype',
            new_name='_old_firstchoice_triptype',
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='preferred_sections',
            new_name='_old_preferred_sections',
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='preferred_triptypes',
            new_name='_old_preferred_triptypes',
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='unavailable_sections',
            new_name='_old_unavailable_sections',
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='unavailable_triptypes',
            new_name='_old_unavailable_triptypes',
        ),
    ]
