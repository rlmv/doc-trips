# Generated by Django 2.0.6 on 2018-06-25 17:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('applications', '0116_auto_20180416_1613'),
        ('incoming', '0035_auto_20180412_1932')
    ]

    operations = [
        migrations.CreateModel(
            name='Gear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('trips_year', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to='core.TripsYear')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GearRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('additional', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('gear', models.ManyToManyField(to='gear.Gear')),
                ('trips_year', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to='core.TripsYear')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
