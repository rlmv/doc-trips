from django.urls import reverse

from fyt.permissions.permissions import Group, GroupRegistry, can_view_database
from fyt.test import FytTestCase


class GroupRegistryTestCase(FytTestCase):
    def test_group_registry(self):
        groups = GroupRegistry({'bus drivers': [can_view_database]})
        self.assertEqual(groups.bus_drivers.name, 'bus drivers')
        self.assertQsEqual(groups.bus_drivers.permissions.all(), [can_view_database()])
        self.assertEqual([g.name for g in groups.all()], ['bus drivers'])

    def test_group_registry_attribute_error(self):
        groups = GroupRegistry({})
        with self.assertRaises(AttributeError):
            groups.olcs

    def test_group_registry_bootstrap(self):
        groups = GroupRegistry({'drivers': [can_view_database]})
        self.assertFalse(Group.objects.filter(name='drivers').exists())
        groups.bootstrap()
        self.assertTrue(Group.objects.filter(name='drivers').exists())


class SetPermissionsViewTestCase(FytTestCase):
    def test_get(self):
        url = reverse('permissions:set_permissions')
        self.app.get(url, user=self.make_director())
