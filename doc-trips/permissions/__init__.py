
from django.contrib.auth.models import Group

from permissions.models import SitePermission

# Should these permission accessors be in a Manager?
def get_permission(codename, name):
    """ Return a the requested SitePermission. """
    permission, created = SitePermission.objects.get_or_create(
        codename=codename, name=name)
    return permission

def initialize_groups_and_permissions():
    """ Set up all permissions used by the site."""

    directors()
    directorate()
    graders()

def can_set_access():
    return get_permission('can_set_access', 
                          'Can assign users permissions and groups')

def can_grade_leader_applications():
    return get_permission('can_grade_leader_applications', 
                          'Can grade leader applications')

def can_create_leader_application():
    return get_permission('can_create_leader_application',
                          'Can create and alter leader app questions')

def can_access_db():
    return get_permission('can_access_db',
                          'Can access trips database')

def can_edit_timetable():
    return get_permission('can_edit_timetable',
                          'Can change critical dates in the timetable')

def can_create_croo_application():
    return get_permission('can_create_croo_application', 
                          'Can create and alter croo app questions')

def can_grade_croo_applications():
    return get_permission('can_grade_croo_applications',
                          'Can grade croo applicaions')

def can_create_applications():
    return get_permission('can_create_applications',
                          'Can create leader and croo applications')


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
                             can_grade_leader_applications(), 
                             can_access_db(), 
                             can_edit_timetable(), 
                             can_grade_croo_applications(), 
                             can_create_applications()]
    directors.save()
    return directors


def directorate():
    directorate, created = Group.objects.get_or_create(name='directorate')
    directorate.permissions = [can_grade_leader_applications(),
                               can_grade_croo_applications()]
    directorate.save()
    return directorate


def tlts():
    # trip leader trainers
    tlts, created = Group.objects.get_or_create(name='tlts')
    tlts.permissions = directorate().permissions + [
                        # can assign trip leaders to trips
                        # can edit leader apps?
                        ]
    tlts.save()
    return tlts


def graders():
    graders, created = Group.objects.get_or_create(name='graders')
    graders.permissions = [can_grade_leader_applications()]
    graders.save()
    return graders
