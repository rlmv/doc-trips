# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('transport', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledTransportation',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date', models.DateField()),
                ('route', models.ForeignKey(to='transport.Route')),
                ('trips_year', models.ForeignKey(editable=False, to='db.TripsYear')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='scheduledtransport',
            name='route',
        ),
        migrations.RemoveField(
            model_name='scheduledtransport',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='ScheduledTransport',
        ),
        migrations.RenameField(
            model_name='stop',
            old_name='primary_route',
            new_name='route',
        ),
        migrations.AddField(
            model_name='route',
            name='category',
            field=models.CharField(choices=[('INTERNAL', 'Internal'), ('EXTERNAL', 'External')], max_length=20, default='INTERNAL'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stop',
            name='category',
            field=models.CharField(choices=[('INTERNAL', 'Internal'), ('EXTERNAL', 'External')], max_length=20, default='INTERNAL'),
            preserve_default=False,
        ),
    ]
