
from django.contrib.auth.models import Group

from user.models import SitePermission


def initialize_groups_and_permissions():
    """ Set up all permissions used by the site."""

    can_grade_applications, created = SitePermission.objects.get_or_create(
                                          codename='can_grade_applications', 
                                          name='Can grade leader applications')

    can_access_db, created = SitePermission.objects.get_or_create(
                                 codename='can_access_db',
                                 name='Can access trips database')
    
    directors, created = Group.objects.get_or_create(name='directors')
    directors.permissions = [can_grade_applications, can_access_db]
    directors.save()

    
    graders, created = Group.objects.get_or_create(name='graders')
    graders.permissions = [can_grade_applications]
    graders.save()

