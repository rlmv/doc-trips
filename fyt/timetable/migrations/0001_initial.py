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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applications_open', models.DateTimeField(default=django.utils.timezone.now)),
                ('applications_close', models.DateTimeField(default=django.utils.timezone.now)),
                ('hide_volunteer_page', models.BooleanField(help_text="Enabling this will hide the database Volunteers page from everyone except directors and trip leader trainers. Use this during grading to prevent graders from seeing applicant's scores.", default=False)),
                ('application_status_available', models.BooleanField(help_text='Turn this on once all decisions have been made regarding Leaders and Croos', default=False)),
                ('leader_assignment_available', models.BooleanField(help_text='Turn this on to let Trip Leaders see information about their assigned trip', default=False)),
                ('trippee_registrations_open', models.DateTimeField(default=django.utils.timezone.now)),
                ('trippee_registrations_close', models.DateTimeField(default=django.utils.timezone.now)),
                ('trippee_assignment_available', models.BooleanField(help_text='Turn this on to let Incoming Students see their trip assignments', default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
