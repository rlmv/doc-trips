# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0005_auto_20150217_0411'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicationdetail',
            name='croo_supplement_doc',
        ),
        migrations.RemoveField(
            model_name='applicationdetail',
            name='leader_supplement_doc',
        ),
        migrations.AddField(
            model_name='applicationdetail',
            name='croo_supplement_questions',
            field=models.FileField(default='', verbose_name='Croo Application questions', upload_to=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicationdetail',
            name='leader_supplement_questions',
            field=models.FileField(default='', verbose_name='Trip Leader Application questions', upload_to=''),
            preserve_default=False,
        ),
    ]
