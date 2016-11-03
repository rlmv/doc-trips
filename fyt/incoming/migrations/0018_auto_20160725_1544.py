# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0013_auto_20151028_1559'),
        ('incoming', '0017_auto_20151230_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionChoice',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('preference', models.CharField(max_length=20, choices=[('PREFER', 'prefer'), ('AVAILABLE', 'available'), ('NOT AVAILABLE', 'not available')])),
                ('registration', models.ForeignKey(to='incoming.Registration')),
                ('section', models.ForeignKey(to='trips.Section')),
            ],
        ),
        migrations.AddField(
            model_name='registration',
            name='section_choice',
            field=models.ManyToManyField(to='trips.Section', through='incoming.SectionChoice'),
        ),
    ]
