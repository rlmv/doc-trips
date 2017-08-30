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
and possibly even the set_acce  ujso 8ss permissions into edit_db? This would
be simpler, but less flexible. However, only directors currently have
the edit_db permission.

"""

# TODO: Should these permission accessors be in a Manager?


def get_permission(codename, name):
    """ Return a the requested SitePermission. """
    permission, _ = SitePermission.objects.get_or_create(
        codename=codename, name=name)
    return permission


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


class GroupRegistry:
    """
    Core registry of all groups and permissions for each group.
    """
    def __init__(self, group_perms):
        self.group_perms = group_perms

    def __getattr__(self, name):
        """Dynamically lookup and return the group, creating it if needed.

        Accessors are mapped to group names, so that ``groups.croo_heads``
        will return the Group object corresponding to the 'croo heads'
        group passed in the permission mapping.
        """
        # Map accessor to group name
        name = name.replace('_', ' ')

        if name in self.group_perms:
            return self.init_group(name)

        raise AttributeError(name)

    def all(self):
        return [self.init_group(name) for name in self.group_perms]

    def init_group(self, name):
        """
        Initialize a group, creating it if necessary, and give it the
        permissions specified.
        """
        permissions = [perm() for perm in self.group_perms[name]]
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.set(permissions)
        return group

    def bootstrap(self):
        """Create all groups."""
        for name in self.group_perms:
            self.init_group(name)


#: Register all groups
groups = GroupRegistry({
    'directors': [
        can_view_database,
        can_edit_database,
        can_edit_settings,
        can_score_applications,
        can_edit_applications_and_assign_trip_leaders,
        can_report_incidents,
        can_edit_trainings],

    'croo heads': [
        can_view_database,
        can_score_applications,
        can_score_as_croo_head],

    'trip leader trainers': [
        can_view_database,
        can_score_applications,
        can_edit_applications_and_assign_trip_leaders,
        can_edit_trainings],

    'outdoor logistics coordinators': [
        can_view_database,
        can_score_applications,
        can_edit_trip_info],

    'directorate': [
        can_view_database,
        can_score_applications],

    'safety leads': [
        can_report_incidents,
        can_edit_trainings],

    'graders': [
        can_score_applications]
    })
