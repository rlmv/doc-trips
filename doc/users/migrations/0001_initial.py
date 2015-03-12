# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DartmouthUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('netid', models.CharField(unique=True, max_length=40)),
                ('email', models.EmailField(verbose_name='email address', max_length=75)),
                ('email2', models.EmailField(null=True, verbose_name='auxiliary email address', max_length=75, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups', related_query_name='user', to='auth.Group', related_name='user_set', blank=True)),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', verbose_name='user permissions', related_query_name='user', to='auth.Permission', related_name='user_set', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
