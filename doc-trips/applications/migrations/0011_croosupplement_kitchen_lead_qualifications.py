# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0010_auto_20150217_1910'),
    ]

    operations = [
        migrations.AddField(
            model_name='croosupplement',
            name='kitchen_lead_qualifications',
            field=models.TextField(blank=True, verbose_name='If you are willing to be a Kitchen Witch/Wizard, please briefly describe your qualifications for the position (eg. Moosilauke Lodge crew spring 2014, experience working in industrial kitchens, experience preparing food for large groups.)', default=''),
            preserve_default=False,
        ),
    ]
