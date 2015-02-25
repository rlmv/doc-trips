# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SitePermissionStub',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
