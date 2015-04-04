# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0054_auto_20150403_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='portalcontent',
            name='CANCELED_description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portalcontent',
            name='CROO_description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portalcontent',
            name='LEADER_WAITLIST_description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portalcontent',
            name='LEADER_description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portalcontent',
            name='PENDING_description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portalcontent',
            name='REJECTED_description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
