# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('raids', '0002_auto_20150909_2313'),
    ]

    operations = [
        migrations.AddField(
            model_name='raid',
            name='user',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='raid',
            field=models.ForeignKey(editable=False, to='raids.Raid', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='trips_year',
            field=models.ForeignKey(to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
