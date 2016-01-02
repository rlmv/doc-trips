# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


targets = [
    'is_exchange',
    'is_transfer',
    'is_international',
    'is_native',
    'is_fysep',
    'regular_exercise',
    'camping_experience',
    'hiking_experience',
    'has_boating_experience',
    'financial_assistance',
    'waiver',
    'doc_membership',
]


def use_boolean_yes_no_fields(apps, schema_editor):
    """Convert CharFields with 'YES', 'NO', values to BooleanFields"""
    Registration = apps.get_model('incoming', 'Registration')

    mapping = {
        'YES': True,
        'NO': False,
        '': None
    }

    for reg in Registration.objects.all():
        for field in targets:
            value = getattr(reg, field)
            setattr(reg, '_' + field, mapping[value])
        reg.save()


def rename_and_remove():
    rename_and_remove = []
    for field in targets:
        rename_and_remove.append(
            migrations.RemoveField(
                model_name='Registration',
                name=field
            ),
        )
        rename_and_remove.append(
            migrations.RenameField(
                model_name='Registration',
                old_name='_' + field,
                new_name=field
            )
        )
    return rename_and_remove


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0016_auto_20151230_1020'),
    ]

    operations = [
        migrations.RunPython(use_boolean_yes_no_fields)
    ] + rename_and_remove()
