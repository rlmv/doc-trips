# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('incoming', '0012_auto_20150904_1014'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('trips_cost', models.PositiveSmallIntegerField()),
                ('doc_membership_cost', models.PositiveSmallIntegerField()),
                ('contact_url', models.URLField(help_text='url of trips directorate contact info')),
                ('trips_year', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='settings',
            unique_together=set([('trips_year',)]),
        ),
    ]
