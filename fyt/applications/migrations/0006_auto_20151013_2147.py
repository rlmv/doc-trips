# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0005_auto_20151013_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='croosupplement',
            name='can_get_certified',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='If you are not certified, are you able to go through the College’s sprinter van & mini-bus driver certification process this spring or summer term?'),
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='college_certified',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='Are you a college-certified driver?'),
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='licensed',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name="Do you have a valid driver's license?"),
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='microbus_certified',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='Are you microbus certified?'),
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='sprinter_certified',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='Are you sprinter van certified?'),
        ),
    ]
