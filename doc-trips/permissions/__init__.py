
from django.contrib.auth.models import Group

from permissions.models import SitePermission

def get_permission(codename, name):
    """ Return a the requested SitePermission. """
    permission, created = SitePermission.objects.get_or_create(
        codename=codename, name=name)
    return permission

def initialize_groups_and_permissions():
    """ Set up all permissions used by the site."""

    directors()
    graders()

def can_set_access():
    return get_permission('can_set_access', 
                          'Can assign users permissions and groups')

def can_grade_applications():
    return get_permission('can_grade_applications', 
                          'Can grade leader applications')

def can_access_db():
    return get_permission('can_access_db',
                          'Can access trips database')


""" # TODO: these might be useful for croos?
can_edit_db, created = get_permission(
codename='can_edit_db',
name='Can edit items in the trips database')
"""
# TODO: can_edit_safety_log


# TODO: should we implement a proxy Group class and move these
# to the model manager? e.g. ProxyGroup.directors() or ProxyGroup.objects.directors()

def directors():    
    directors, created = Group.objects.get_or_create(name='directors')
    directors.permissions = [can_set_access(), 
                             can_grade_applications(), 
                             can_access_db()]
    directors.save()
    return directors

def graders():
    graders, created = Group.objects.get_or_create(name='graders')
    graders.permissions = [can_grade_applications()]
    graders.save()
    return graders
