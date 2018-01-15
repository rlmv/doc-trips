# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('transport', '0001_initial'),
        ('trips', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stoporder',
            name='trip',
            field=models.ForeignKey(to='trips.Trip', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stoporder',
            name='trips_year',
            field=models.ForeignKey(to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='stoporder',
            unique_together=set([('trips_year', 'bus', 'trip')]),
        ),
        migrations.AddField(
            model_name='stop',
            name='route',
            field=models.ForeignKey(related_name='stops', on_delete=django.db.models.deletion.PROTECT, blank=True, to='transport.Route', null=True, help_text='default bus route'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stop',
            name='trips_year',
            field=models.ForeignKey(to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduledtransport',
            name='route',
            field=models.ForeignKey(to='transport.Route', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduledtransport',
            name='trips_year',
            field=models.ForeignKey(to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='scheduledtransport',
            unique_together=set([('trips_year', 'route', 'date')]),
        ),
        migrations.AddField(
            model_name='route',
            name='trips_year',
            field=models.ForeignKey(to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='route',
            name='vehicle',
            field=models.ForeignKey(to='transport.Vehicle', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='externalbus',
            name='route',
            field=models.ForeignKey(to='transport.Route', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='externalbus',
            name='section',
            field=models.ForeignKey(to='trips.Section', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='externalbus',
            name='trips_year',
            field=models.ForeignKey(to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='externalbus',
            unique_together=set([('trips_year', 'route', 'section')]),
        ),
    ]
