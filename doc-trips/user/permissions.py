
from django.contrib.auth.models import Group

from user.models import SitePermission


def initialize_groups_and_permissions():
    """ Set up all permissions used by the site."""

    directors()
    graders()

def can_set_access():
    can_set_access, created = SitePermission.objects.get_or_create(
        codename='can_allow_access', name='Can assign users permissions and groups')
    
    return can_set_access

def can_grade_applications():
    can_grade_applications, created = SitePermission.objects.get_or_create(
                                          codename='can_grade_applications', 
                                          name='Can grade leader applications')
    return can_grade_applications

def can_access_db():
    can_access_db, created = SitePermission.objects.get_or_create(
                                 codename='can_access_db',
                                 name='Can access trips database')
    return can_access_db

""" # TODO: these might be useful for croos?
can_edit_db, created = SitePermission.objects.get_or_create(
codename='can_edit_db',
name='Can edit items in the trips database')
"""
# TODO: can_edit_safety_log

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
