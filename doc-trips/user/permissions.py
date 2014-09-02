
from django.contrib.auth.models import Group

from user.models import SitePermission


def initialize_groups_and_permissions():
    """ Set up all permissions used by the site."""

    can_set_access, created = SitePermission.objects.get_or_create(
        codename='can_allow_access', name='Can assign users permissions and groups')

    can_grade_applications, created = SitePermission.objects.get_or_create(
                                          codename='can_grade_applications', 
                                          name='Can grade leader applications')

    can_access_db, created = SitePermission.objects.get_or_create(
                                 codename='can_access_db',
                                 name='Can access trips database')

    """ # TODO: these might be useful for croos?
    can_edit_db, created = SitePermission.objects.get_or_create(
        codename='can_edit_db',
        name='Can edit items in the trips database')
    """

    # TODO: can_edit_safety_log
    
    directors, created = Group.objects.get_or_create(name='directors')
    directors.permissions = [can_set_access, can_grade_applications, can_access_db]
    directors.save()
        
    graders, created = Group.objects.get_or_create(name='graders')
    graders.permissions = [can_grade_applications]
    graders.save()

