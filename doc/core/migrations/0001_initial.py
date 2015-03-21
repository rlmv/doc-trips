# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Globals',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('trips_cost', models.PositiveSmallIntegerField()),
                ('doc_membership_cost', models.PositiveSmallIntegerField()),
                ('contact_url', models.URLField(help_text='url of trips_directorate contact info')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
