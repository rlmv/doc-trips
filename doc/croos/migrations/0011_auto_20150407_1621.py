# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0010_auto_20150310_1152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='_crooapplicationgrade',
            name='application',
        ),
        migrations.RemoveField(
            model_name='_crooapplicationgrade',
            name='grader',
        ),
        migrations.RemoveField(
            model_name='_crooapplicationgrade',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='_CrooApplicationGrade',
        ),
        migrations.RemoveField(
            model_name='crooapplication',
            name='applicant',
        ),
        migrations.RemoveField(
            model_name='crooapplication',
            name='trips_year',
        ),
        migrations.RemoveField(
            model_name='crooapplicationanswer',
            name='application',
        ),
        migrations.DeleteModel(
            name='CrooApplication',
        ),
        migrations.RemoveField(
            model_name='crooapplicationanswer',
            name='question',
        ),
        migrations.RemoveField(
            model_name='crooapplicationanswer',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='CrooApplicationAnswer',
        ),
        migrations.RemoveField(
            model_name='crooapplicationquestion',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='CrooApplicationQuestion',
        ),
    ]
