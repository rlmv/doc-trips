# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0012_auto_20150218_1846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='croosupplement',
            name='application',
            field=models.OneToOneField(editable=False, to='applications.GeneralApplication', related_name='croo_supplement'),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='applicant',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='leadersupplement',
            name='application',
            field=models.OneToOneField(editable=False, to='applications.GeneralApplication', related_name='leader_supplement'),
        ),
    ]
