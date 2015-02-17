# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0008_auto_20150217_0610'),
    ]

    operations = [
        migrations.RenameField(
            model_name='applicationinformation',
            old_name='croo_application_introduction',
            new_name='croo_application_information',
        ),
        migrations.RenameField(
            model_name='applicationinformation',
            old_name='leader_application_introduction',
            new_name='leader_application_information',
        ),
    ]
