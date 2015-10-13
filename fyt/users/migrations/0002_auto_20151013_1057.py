# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dartmouthuser',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='dartmouthuser',
            name='email2',
            field=models.EmailField(max_length=254, blank=True, null=True, verbose_name='auxiliary email address'),
        ),
        migrations.AlterField(
            model_name='dartmouthuser',
            name='groups',
            field=models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', related_name='user_set', blank=True, related_query_name='user', verbose_name='groups'),
        ),
    ]
