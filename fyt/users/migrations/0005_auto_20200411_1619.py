# Generated by Django 2.2.11 on 2020-04-11 20:19
import re
from django.db import migrations
from fyt.dartdm.lookup import lookup_dartdm

current_class_years = ['19', '20', '21', '22', '23']

def is_staff_or_current_student(user):
    email = user.email
    classYearRegex = re.findall(r'\d{2}@Dartmouth.edu', email, re.IGNORECASE)

    # Return True if classYear couldn't be parsed
    if len(classYearRegex) == 0:
        return True

    classYear = classYearRegex[0][:2]
    return classYear in current_class_years


def get_newest_name(apps, schema_editor):
    User = apps.get_model('users', 'DartmouthUser')
    for localUser in User.objects.all():

        if is_staff_or_current_student(localUser):
            print('Retrieving user with netid', localUser.netid, 'and name', localUser.name)
            dartResponse = lookup_dartdm(localUser.netid)
            dartdmUser = dartResponse[0] if len(dartResponse) != 0 else None

            if dartdmUser is None:
                print('Error, netid', localUser.netid, 'not found')
            elif localUser.name != dartdmUser['name']:
                print('Remote name ', dartdmUser['name'], ' did not match localUser name', localUser.name)
                print('Setting to updated name')
                localUser.name = dartdmUser['name']
                localUser.save()




class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_dartmouthuser_email2'),
    ]

    operations = [
        migrations.RunPython(get_newest_name)
    ]
