# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0009_auto_20150217_0611'),
    ]

    operations = [
        migrations.RenameField(
            model_name='applicationinformation',
            old_name='croo_application_information',
            new_name='croo_info',
        ),
        migrations.RenameField(
            model_name='applicationinformation',
            old_name='leader_application_information',
            new_name='leader_info',
        ),
        migrations.AddField(
            model_name='applicationinformation',
            name='application_header',
            field=models.TextField(help_text='This will be displayed at the top of all application pages', default='', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicationinformation',
            name='general_info',
            field=models.TextField(help_text='This will be displayed at the top of the General Information tab', default='', blank=True),
            preserve_default=False,
        ),
    ]
