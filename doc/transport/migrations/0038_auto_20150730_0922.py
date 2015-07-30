# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def delete_stoporders(apps, schema_editor):
    StopOrder = apps.get_model('transport', 'StopOrder')
    StopOrder.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0037_auto_20150729_2246'),
    ]

    operations = [
        migrations.RunPython(delete_stoporders)
    ]
