# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import doc.croos.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '__first__'),
        ('croos', '0008_auto_20150216_0239'),
    ]

    operations = [
        migrations.CreateModel(
            name='_CrooApplicationGrade',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('grade', models.IntegerField(validators=[doc.croos.models.validate_grade])),
                ('comments', models.TextField()),
                ('application', models.ForeignKey(to='croos.CrooApplication', related_name='grades')),
                ('grader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('trips_year', models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='crooapplicationgrade',
            name='application',
        ),
        migrations.RemoveField(
            model_name='crooapplicationgrade',
            name='grader',
        ),
        migrations.RemoveField(
            model_name='crooapplicationgrade',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='CrooApplicationGrade',
        ),
    ]
