# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0008_auto_20140915_1559'),
        ('leader', '0018_auto_20140913_1657'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('info', models.CharField(max_length=255)),
                ('leader', models.ForeignKey(to='leader.LeaderApplication')),
                ('section', models.ForeignKey(to='trip.Section')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='through_sections',
            field=models.ManyToManyField(blank=True, through='leader.SectionPreferences', to='trip.Section'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='dietary_restrictions',
            field=models.TextField(blank=True, verbose_name='Do you have any dietary restrictions or allergies that we should know about?'),
        ),
    ]
