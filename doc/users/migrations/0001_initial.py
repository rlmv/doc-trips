# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DartmouthUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('netid', doc.users.models.NetIdField(unique=True, max_length=20)),
                ('did', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=75, verbose_name='email address')),
                ('email2', models.EmailField(max_length=75, null=True, blank=True, verbose_name='auxiliary email address')),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('groups', models.ManyToManyField(related_name='user_set', blank=True, to='auth.Group', verbose_name='groups', related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', blank=True, to='auth.Permission', verbose_name='user permissions', related_query_name='user', help_text='Specific permissions for this user.')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
    ]
