# Generated by Django 2.0.3 on 2018-03-23 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0084_auto_20180323_1418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='score',
            name='score',
        ),
    ]