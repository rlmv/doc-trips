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
    permission, _ = SitePermission.objects.get_or_create(
        codename=codename, name=name)
    return permission


def initialize_groups_and_permissions():
    """ Set up all permissions used by the site."""
    trip_leader_trainers()
    directors()
    directorate()
    croo_heads()
    graders()
    safety_leads()
    olcs()


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

def can_edit_settings():
    return get_permission('can_edit_settings',
                          'Can change database settings')

def can_score_applications():
    return get_permission('can_score_applications', 'Can score applications')

def can_score_as_croo_head():
    return get_permission('can_score_as_croo_head',
                          'Can score applications reserved for croo heads')

def can_edit_applications_and_assign_trip_leaders():
    """ Permission specific to TLTs so they can tweak leader applications """
    return get_permission('can_edit_applications_and_assign_leaders',
                          'Can change apps in DB and assign leaders')

def can_edit_trainings():
    """Permissions allowing TLTs and directorate to update trainings."""
    return get_permission('can_edit_trainings', 'Can edit trainings')

def can_edit_trip_info():
    """ Permissions to allow olcs users to edit trip itineraries """
    return get_permission('can_edit_trip_info', 'Can edit trip itineraries')

def can_report_incidents():
    return get_permission('can_report_incidents',
                          'Can report incidents in the safety log')

# TODO: should we implement a proxy Group class and move these
# to the model manager? e.g. ProxyGroup.directors() or ProxyGroup.objects.directors()

def directors():
    directors, _ = Group.objects.get_or_create(name='directors')
    directors.permissions.set([
        can_view_database(),
        can_edit_database(),
        can_edit_settings(),
        can_score_applications(),
        can_edit_applications_and_assign_trip_leaders(),
        can_report_incidents(),
        can_edit_trainings(),
    ])
    return directors


def directorate():
    directorate, _ = Group.objects.get_or_create(name='directorate')
    directorate.permissions.set([
        can_view_database(),
        can_score_applications(),
    ])
    return directorate


def croo_heads():
    heads, _ = Group.objects.get_or_create(name='croo heads')
    heads.permissions.set([
        can_view_database(),
        can_score_applications(),
        can_score_as_croo_head(),
    ])
    return heads


def trip_leader_trainers():
    # trip leader trainers
    tlts, _ = Group.objects.get_or_create(name='trip leader trainers')
    tlts.permissions.set([
        can_view_database(),
        can_score_applications(),
        can_edit_applications_and_assign_trip_leaders(),
        can_edit_trainings(),
    ])
    return tlts


def olcs():
    olcs, _ = Group.objects.get_or_create(name='outdoor logistics coordinators')
    olcs.permissions.set([
        can_view_database(),
        can_score_applications(),
        can_edit_trip_info(),
    ])
    return olcs


def safety_leads():
    leads, _ = Group.objects.get_or_create(name='safety leads')
    leads.permissions.set([
        can_report_incidents(),
        can_edit_trainings(),
    ])
    return leads


def graders():
    graders, _ = Group.objects.get_or_create(name='graders')
    graders.permissions.set([
        can_score_applications(),
    ])
    return graders
