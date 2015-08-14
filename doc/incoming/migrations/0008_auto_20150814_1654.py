# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0007_auto_20150813_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incomingstudent',
            name='hide_med_info',
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='show_med_info',
            field=models.BooleanField(verbose_name='Show registration med info?', help_text="Medical information in this trippee's registration will be displayed in leader and croo packets. (This information is hidden by default.)", default=False),
            preserve_default=True,
        ),
    ]
