# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0015_auto_20150224_2104'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trippees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trippee',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('decline_reason', models.CharField(max_length=50)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrippeeInfo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('did', models.CharField(max_length=30)),
                ('ethnicity_code', models.CharField(max_length=1)),
                ('gender_code', models.CharField(max_length=1)),
                ('incoming_status', models.CharField(choices=[('EXCHANGE', 'Exchange'), ('TRANSFER', 'Transfer'), ('FIRSTYEAR', 'First Year')], max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('dartmouth_email', models.EmailField(max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='trippee',
            name='info',
            field=models.ForeignKey(editable=False, to='trippees.TrippeeInfo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trippee',
            name='registration',
            field=models.ForeignKey(editable=False, to='trippees.TrippeeRegistration'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trippee',
            name='trip_assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='trips.ScheduledTrip'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trippee',
            name='user',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trippeeregistration',
            name='camping_experience',
            field=models.CharField(choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever spent a night camping in the outdoors?', max_length=2),
        ),
        migrations.AlterField(
            model_name='trippeeregistration',
            name='financial_assistance',
            field=models.CharField(choices=[('YES', 'yes'), ('NO', 'no')], verbose_name="Are you requesting financial assistance from DOC Trips? If 'yes' we will contact you in July with more information about your financial assistance.", max_length=2),
        ),
        migrations.AlterField(
            model_name='trippeeregistration',
            name='has_boating_experience',
            field=models.CharField(choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever been on an overnight or extended canoe or kayak trip?', max_length=2),
        ),
        migrations.AlterField(
            model_name='trippeeregistration',
            name='hiking_experience',
            field=models.CharField(choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever hiked or climbed with a pack of at least 20-30 pounds (10-15 kilograms)?', max_length=2),
        ),
        migrations.AlterField(
            model_name='trippeeregistration',
            name='waiver',
            field=models.CharField(choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver & acknowledgement.', max_length=2),
        ),
    ]
