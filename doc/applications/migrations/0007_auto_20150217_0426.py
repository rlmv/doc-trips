# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('applications', '0006_auto_20150217_0419'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationInformation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('leader_supplement_questions', models.FileField(upload_to='', verbose_name='Trip Leader Application questions')),
                ('croo_supplement_questions', models.FileField(upload_to='', verbose_name='Croo Application questions')),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear', editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='applicationdetail',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='applicationdetail',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='ApplicationDetail',
        ),
        migrations.AlterUniqueTogether(
            name='applicationinformation',
            unique_together=set([('trips_year',)]),
        ),
    ]
