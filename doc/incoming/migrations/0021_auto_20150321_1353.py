# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0020_auto_20150321_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='is_athlete',
            field=models.CharField(choices=[('NO', 'No'), ('ALPINE_SKIING', 'Alpine Skiing'), ('FOOTBALL', 'Football'), ('MENS_SOCCER', "Men's Soccer"), ('WOMENS_SOCCER', "Women's Soccer"), ('FIELD_HOCKEY', 'Field Hockey'), ('VOLLEYBALL', 'Volleyball'), ('MENS_HEAVYWEIGHT_CREW', "Men's Heavyweight Crew"), ('MENS_LIGHTWEIGHT_CREW', "Men's Lightweight Crew"), ('WOMENS_CREW', "Women's Crew"), ('MENS_CROSS_COUNTRY', "Men's Cross Country"), ('WOMENS_CROSS_COUNTRY', "Women's Cross Country"), ('MENS_GOLF', "Men's Golf"), ('WOMENS_GOLF', "Women's Golf"), ('MENS_TENNIS', "Men's Tennis"), ('WOMENS_TENNIS', "Women's Tennis"), ('MENS_RUGBY', "Men's Rugby"), ('WOMENS_RUGBY', "Women's Rugby"), ('SAILING', 'Sailing'), ('MENS_WATER_POLO', "Men's Water Polo")], blank=True, help_text="Each team has its own pre-season schedule. We are in close contact with fall coaches and will assign you to a trip section that works well for the team's pre-season schedule.", max_length=100, verbose_name='Are you a Fall varsity athlete (or Rugby or Water Polo)?'),
        ),
    ]
