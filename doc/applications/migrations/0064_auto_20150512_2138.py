# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def move_trainings_to_GeneralApplication(apps, schema_editor):

    GeneralApplication = apps.get_model("applications", "GeneralApplication")
    for ga in GeneralApplication.objects.all():
        ls = ga.leader_supplement
        ga.community_building = ls.community_building
        ga.risk_management = ls.risk_management
        ga.wilderness_skills = ls.wilderness_skills
        ga.save()

class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0063_auto_20150512_2128'),
    ]

    operations = [
        migrations.RunPython(move_trainings_to_GeneralApplication)
    ]
