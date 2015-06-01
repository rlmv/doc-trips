# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, connection
from django.db.utils import OperationalError

def reset_sequences(apps, schema_editor):

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT setval('auth_group_id_seq', (SELECT MAX(id) FROM auth_group) + 1)")
        cursor.execute("SELECT setval('auth_permission_id_seq', (SELECT MAX(id) FROM auth_permission) + 1)")
    except OperationalError as exc:
        print(exc)


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0004_auto_20150305_1940'),
    ]

    operations = [
        migrations.RunPython(reset_sequences),
    ]
