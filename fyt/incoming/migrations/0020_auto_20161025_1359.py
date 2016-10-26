# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fyt.incoming.models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0013_auto_20151028_1559'),
        ('incoming', '0019_auto_20160725_1617'),
    ]

    operations = [
        migrations.CreateModel(
            name='TripTypeChoice',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('preference', models.CharField(max_length=20, choices=[('PREFER', 'prefer'), ('AVAILABLE', 'available'), ('NOT AVAILABLE', 'not available')])),
                ('registration', models.ForeignKey(to='incoming.Registration')),
                ('triptype', models.ForeignKey(to='trips.TripType')),
            ],
        ),
        migrations.AddField(
            model_name='registration',
            name='triptype_choice',
            field=fyt.incoming.models.TripTypeChoiceField(to='trips.TripType', through='incoming.TripTypeChoice'),
        ),
    ]
