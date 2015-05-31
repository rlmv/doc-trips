# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def lowercase_netids(apps, schema_editor):
    DartmouthUser = apps.get_model('users', 'DartmouthUser')
    for user in DartmouthUser.objects.all():
        user.netid = user.netid.lower()
        user.save()
        print('lowercasing user %s %s' % (user, user.netid))

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20150531_1411'),
    ]

    operations = [
        migrations.RunPython(lowercase_netids)
    ]
