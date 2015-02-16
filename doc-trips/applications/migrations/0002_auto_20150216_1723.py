# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='croosupplement',
            old_name='file',
            new_name='document',
        ),
        migrations.RenameField(
            model_name='croosupplement',
            old_name='safety_dork',
            new_name='safety_lead',
        ),
        migrations.RenameField(
            model_name='croosupplement',
            old_name='safety_dork_qualified',
            new_name='safety_lead_qualified',
        ),
        migrations.RenameField(
            model_name='leadersupplement',
            old_name='file',
            new_name='supplement',
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='kitchen_lead_willing',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='safety_lead_willing',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
