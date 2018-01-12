# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0013_auto_20151028_1559'),
        ('applications', '0010_generalapplication_leadership_style'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaderSectionChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('preference', models.CharField(choices=[('PREFER', 'prefer'), ('AVAILABLE', 'available'), ('NOT AVAILABLE', 'not available')], max_length=20)),
                ('application', models.ForeignKey(to='applications.LeaderSupplement', on_delete=models.CASCADE)),
                ('section', models.ForeignKey(to='trips.Section', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='LeaderTripTypeChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('preference', models.CharField(choices=[('PREFER', 'prefer'), ('AVAILABLE', 'available'), ('NOT AVAILABLE', 'not available')], max_length=20)),
                ('application', models.ForeignKey(to='applications.LeaderSupplement', on_delete=models.CASCADE)),
                ('triptype', models.ForeignKey(to='trips.TripType', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='section_choice',
            field=models.ManyToManyField(through='applications.LeaderSectionChoice', to='trips.Section'),
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='triptype_choice',
            field=models.ManyToManyField(through='applications.LeaderTripTypeChoice', to='trips.TripType'),
        ),
        migrations.AlterUniqueTogether(
            name='leadertriptypechoice',
            unique_together=set([('application', 'triptype')]),
        ),
        migrations.AlterUniqueTogether(
            name='leadersectionchoice',
            unique_together=set([('application', 'section')]),
        ),
    ]
