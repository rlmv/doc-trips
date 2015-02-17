# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('applications', '0004_auto_20150216_1805'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('leader_supplement_doc', models.FileField(upload_to='')),
                ('croo_supplement_doc', models.FileField(upload_to='')),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='applicationdetail',
            unique_together=set([('trips_year',)]),
        ),
    ]
