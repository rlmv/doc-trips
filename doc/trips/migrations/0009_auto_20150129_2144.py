# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0008_triptemplate_return_route'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptemplate',
            name='return_route',
            field=models.ForeignKey(to='transport.Route', null=True, related_name='returning_trips'),
        ),
    ]
