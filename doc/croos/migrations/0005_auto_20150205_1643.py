# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0004_auto_20150204_1628'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='crooapplicationanswer',
            options={'ordering': ['question__ordering']},
        ),
        migrations.AlterModelOptions(
            name='crooapplicationquestion',
            options={'ordering': ['ordering']},
        ),
    ]
