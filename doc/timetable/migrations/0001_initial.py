# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('leader_application_open', models.DateTimeField(default=django.utils.timezone.now)),
                ('leader_application_closed', models.DateTimeField(default=django.utils.timezone.now)),
                ('leader_assignment_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('trippee_registration_open', models.DateTimeField(default=django.utils.timezone.now)),
                ('trippee_registration_closed', models.DateTimeField(default=django.utils.timezone.now)),
                ('trippee_assignment_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('migration_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
