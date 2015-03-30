# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('incoming', '0007_auto_20150312_1031'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollegeInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('did', models.CharField(max_length=30)),
                ('ethnicity_code', models.CharField(max_length=1)),
                ('gender_code', models.CharField(max_length=1)),
                ('incoming_status', models.CharField(max_length=20, choices=[('EXCHANGE', 'Exchange'), ('TRANSFER', 'Transfer'), ('FIRSTYEAR', 'First Year')])),
                ('email', models.EmailField(max_length=254)),
                ('dartmouth_email', models.EmailField(max_length=254)),
                ('trips_year', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='trippeeinfo',
            name='trips_year',
        ),
        migrations.AlterField(
            model_name='trippee',
            name='info',
            field=models.OneToOneField(editable=False, related_name='trippee', to='incoming.CollegeInfo'),
        ),
        migrations.DeleteModel(
            name='TrippeeInfo',
        ),
    ]
