# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0024_auto_20161027_1737'),
    ]

    operations = [
        migrations.RenameModel('SectionChoice',
                               'RegistrationSectionChoice'),
        migrations.RenameModel('TripTypeChoice',
                               'RegistrationTripTypeChoice')
    ]
