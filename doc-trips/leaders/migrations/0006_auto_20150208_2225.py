# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('leaders', '0005_auto_20150206_2329'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaderApplicationAnswer',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('answer', models.TextField()),
                ('application', models.ForeignKey(related_name='answers', to='leaders.LeaderApplication', editable=False)),
            ],
            options={
                'ordering': ['question__ordering'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaderApplicationQuestion',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('question', models.TextField()),
                ('ordering', models.IntegerField()),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['ordering'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='leaderapplicationanswer',
            name='question',
            field=models.ForeignKey(to='leaders.LeaderApplicationQuestion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplicationanswer',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='phone',
            field=models.CharField(verbose_name='Phone Number', max_length=255),
        ),
    ]
