# Generated by Django 2.0.2 on 2018-03-04 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0074_auto_20180302_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteer',
            name='what_do_you_like_to_study',
            field=models.CharField(blank=True, max_length=255, verbose_name='What do you like to study?'),
        ),
    ]
