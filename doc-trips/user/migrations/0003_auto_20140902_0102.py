# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('user', '0002_globalpermission'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GlobalPermission',
        ),
        migrations.CreateModel(
            name='SitePermission',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.permission',),
        ),
    ]
