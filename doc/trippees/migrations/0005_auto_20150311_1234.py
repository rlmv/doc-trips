# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trippees', '0004_auto_20150310_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='trippeeregistration',
            name='user',
            field=models.ForeignKey(editable=False, default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='trippee',
            name='decline_reason',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='trippee',
            name='info',
            field=models.OneToOneField(null=True, editable=False, to='trippees.TrippeeInfo', related_name='trippee'),
        ),
        migrations.AlterField(
            model_name='trippee',
            name='registration',
            field=models.OneToOneField(related_name='trippee', editable=False, to='trippees.TrippeeRegistration'),
        ),
        migrations.AlterField(
            model_name='trippee',
            name='trip_assignment',
            field=models.ForeignKey(related_name='trippees', to='trips.ScheduledTrip', null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
