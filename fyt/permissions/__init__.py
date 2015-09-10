
from django.contrib.auth.models import Group

from fyt.permissions.models import SitePermission

"""
Be careful changing the names of these permissions -- there can
be Unique constraint issues. You may need to add a data migration
to delete the offending historic permissions if this happens. 
Fortunately this doesn't seem to be an issue since permissions
for any given user are tied to groups, not the specific 
SitePermission.

TODO: should we consolidate the create_application, edit_timetable, 
and possibly even the set_access permissions into edit_db? This would 
be simpler, but less flexible. However, only directors currently have 
the edit_db permission.

"""

# TODO: Should these permission accessors be in a Manager?


def get_permission(codename, name):
    """ Return a the requested SitePermission. """
    permission, created = SitePermission.objects.get_or_create(
        codename=codename, name=name)
    return permission


def initialize_groups_and_permissions():
    """ Set up all permissions used by the site."""
    trip_leader_trainers()
    directors()
    directorate()
    graders()
    safety_leads()


def can_set_access():
    return get_permission('can_set_access', 
                          'Can assign users permissions and groups')

def can_view_database():
    return get_permission('can_view_db',
                          'Can view the trips database')

def can_edit_database():
    """ 
    Implies can_view_db permissions. It's assumed that if you can edit, 
    you can also view an object.
    """
    return get_permission('can_edit_db',
                          'Can edit objects in the trips database')

def can_edit_timetable():
    return get_permission('can_edit_timetable',
                          'Can change critical dates in the timetable')

def can_create_applications():
    return get_permission('can_create_applications',
                          'Can create leader and croo applications')

def can_grade_leader_applications():
    return get_permission('can_grade_leader_applications', 
                          'Can grade leader applications')

def can_grade_croo_applications():
    return get_permission('can_grade_croo_applications',
                          'Can grade croo applicaions')

def can_edit_applications_and_assign_trip_leaders():
    """ Permission specific to TLTs so they can tweak leader applications """
    return get_permission('can_edit_applications_and_assign_leaders', 
                          'Can change apps in DB and assign leaders')

def can_report_incidents():
    return get_permission('can_report_incidents',
                          'Can report incidents in the safety log')

# TODO: should we implement a proxy Group class and move these
# to the model manager? e.g. ProxyGroup.directors() or ProxyGroup.objects.directors()

def directors():    
    directors, created = Group.objects.get_or_create(name='directors')
    directors.permissions = [
        can_set_access(), 
        can_view_database(),
        can_edit_database(),
        can_edit_timetable(), 
        can_grade_croo_applications(),
        can_grade_leader_applications(), 
        can_create_applications(), 
        can_edit_applications_and_assign_trip_leaders(),
        can_report_incidents()
    ]
    directors.save()
    return directors


def directorate():
    directorate, created = Group.objects.get_or_create(name='directorate')
    directorate.permissions = [
        can_view_database(),
        can_grade_leader_applications(),
        can_grade_croo_applications(),
    ]
    directorate.save()
    return directorate


def trip_leader_trainers():
    # trip leader trainers
    tlts, created = Group.objects.get_or_create(name='trip leader trainers')
    tlts.permissions = [
        can_view_database(),
        can_grade_leader_applications(),
        can_edit_applications_and_assign_trip_leaders(),
    ]
    tlts.save()
    return tlts


def safety_leads():
    leads, _ = Group.objects.get_or_create(name='safety leads')
    leads.permissions = [
        can_report_incidents()
    ]
    leads.save()
    return leads


def graders():
    graders, created = Group.objects.get_or_create(name='graders')
    graders.permissions = [
        can_grade_leader_applications(),
    ]
    graders.save()
    return graders

