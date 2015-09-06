# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0065_auto_20150512_2212'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='generalapplication',
            options={'ordering': ['applicant']},
        ),
        migrations.AlterField(
            model_name='croosupplement',
            name='kitchen_lead_qualifications',
            field=models.TextField(verbose_name='If you are willing to be a Kitchen Witch/Wizard, please briefly describe your qualifications for the position', help_text='(eg. on Moosilauke Lodge crew spring 2014, experience working in industrial kitchens, experience preparing and organizing food for large groups)'),
        ),
    ]
