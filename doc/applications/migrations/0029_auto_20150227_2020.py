# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0028_auto_20150227_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationinformation',
            name='croo_supplement_questions',
            field=models.FileField(upload_to='', verbose_name='Croo Application questions', help_text='.docx file'),
        ),
        migrations.AlterField(
            model_name='applicationinformation',
            name='leader_supplement_questions',
            field=models.FileField(upload_to='', verbose_name='Leader Application questions', help_text='.docx file'),
        ),
    ]
