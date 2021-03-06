# Generated by Django 2.1 on 2018-08-22 12:06

from django.db import migrations


def move_description_data(apps, schema_editor):
    TripTemplate = apps.get_model('trips', 'TripTemplate')
    TripTemplateDescription = apps.get_model('trips', 'TripTemplateDescription')

    for tt in TripTemplate.objects.all():
        tt.description = TripTemplateDescription.objects.create(
            trips_year=tt.trips_year,
            intro=tt.desc_intro,
            day1=tt.desc_day1,
            day2=tt.desc_day2,
            day3=tt.desc_day3,
            conclusion=tt.desc_conc,
            revisions=tt.revisions)
        tt.save()


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0022_auto_20180822_0805'),
    ]

    operations = [
        migrations.RunPython(move_description_data)
    ]
