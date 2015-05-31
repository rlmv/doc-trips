# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def lowercase_netids(apps, schema_editor):

    Registration = apps.get_model('incoming', 'Registration')
    IncomingStudent = apps.get_model('incoming', 'IncomingStudent')
    for student in IncomingStudent.objects.all():
        student.netid = student.netid.lower()
        print('lowercasing incoming student %s %s' % (student, student.netid))
        try:
            student.registration = Registration.objects.get(user__netid=student.netid,
                                                            trips_year=student.trips_year)
            print('linking student %s to registration %s' % (student, student.registration))
        except Registration.DoesNotExist:
            pass
        student.save()


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0037_auto_20150531_1411'),
        ('users', '0006_auto_20150531_1425'),
    ]

    operations = [
        migrations.RunPython(lowercase_netids)
    ]
