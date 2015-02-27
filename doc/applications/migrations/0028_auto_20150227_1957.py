# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0027_auto_20150225_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationinformation',
            name='croo_supplement_questions',
            field=models.FileField(blank=True, verbose_name='Croo Application questions', help_text='.docx file', upload_to=''),
        ),
        migrations.AlterField(
            model_name='applicationinformation',
            name='leader_supplement_questions',
            field=models.FileField(blank=True, verbose_name='Leader Application questions', help_text='.docx file', upload_to=''),
        ),
    ]
