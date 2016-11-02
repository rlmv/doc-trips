from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.utils.deprecation import CallableFalse, CallableTrue

from fyt.dartdm.lookup import lookup_email, EmailLookupException

MAX_NETID_LENGTH = 20


class DartmouthUserManager(BaseUserManager):
    """
    Object manager for DartmouthUser
    """
    def get_or_create_by_netid(self, netid, name):
        """
        Return the user with netid.

        Create the user if necessary. Does not search via name, since names
        from different sources (CAS, DartDm lookup) can be slightly different.
        """
        try:
            user = self.get(netid=netid)
            created = False
        except self.model.DoesNotExist:
            user = self.create_user(netid, name=name)
            created = True

        return (user, created)

    def create_user(self, netid, name, email=None):
        """
        Create a user. Try and lookup user's email in the Dartmouth Directory
        manager. If not found email is left empty.
        """
        if email is None:
            try:
                email = lookup_email(netid)
            except EmailLookupException:
                email = ''

        return self.create(netid=netid, email=email, name=name)

    def create_superuser(self, **kwargs):
        raise Exception("create_superuser not implemented. "
                        "Use 'manage.py setsuperuser' instead.")

    def create_user_without_netid(self, name, email):
        """
        Create a user without a netid.

        Used for non-student registrations. The name is used as a stand-in
        netid, truncated if if is too long.
        """
        netid = name

        if len(netid) > MAX_NETID_LENGTH:
            netid = netid[:MAX_NETID_LENGTH]

        return self.create(netid=netid, name=name, email=email)


class NetIdField(models.CharField):
    """
    Saves NetIds as lowercase for easy comparison.
    """
    description = "A field to hold a Dartmouth WebAuth Netid"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = MAX_NETID_LENGTH
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Handle uppercase ids
        """
        value = super().to_python(value)
        if value is not None:
            return value.lower()

    def pre_save(self, model_instance, add):
        """
        Update lowercase ids on the instance before saving
        """
        value = getattr(model_instance, self.attname).lower()
        setattr(model_instance, self.attname, value)
        return value


class DartmouthUser(PermissionsMixin):

    objects = DartmouthUserManager()

    netid = NetIdField(unique=True)
    email = models.EmailField('email address')
    name = models.CharField(max_length=255, db_index=True)

    last_login = models.DateTimeField('last login', blank=True, null=True)

    class Meta:
        ordering = ['name']

    USERNAME_FIELD = 'netid'
    REQUIRED_FIELDS = ['email', 'name']

    def get_short_name(self):
        return self.name

    def get_full_name(self):
        return self.name

    def get_username(self):
        return self.netid

    # Return the `CallableBool` objects to support various versions of
    # `is_authenticated` and `is_anonymous` in dependencies.
    # TODO: fallback to straight properties

    @property
    def is_authenticated(self):
        return CallableTrue

    @property
    def is_anonymous(self):
        return CallableFalse

    @property
    def is_active(self):
        return True

    @property
    def is_staff(self):
        return self.is_superuser

    def __str__(self):
        return str(self.name)
