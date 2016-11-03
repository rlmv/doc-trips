# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0023_auto_20161027_1314'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sectionchoice',
            unique_together=set([('registration', 'section')]),
        ),
        migrations.AlterUniqueTogether(
            name='triptypechoice',
            unique_together=set([('registration', 'triptype')]),
        ),
    ]
