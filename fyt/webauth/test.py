import unittest

from fyt.test import FytTestCase
from fyt.webauth.views import host_url, protocol


class GroupPermissionsTest(FytTestCase):

    def test_group_permissions_work_with_custom_backend(self):
        # None of the permissions worked when the backend
        # did not inherit from ModelBackend

        # the director group SHOULD have a number of permissions
        user = self.mock_director()
        self.assertNotEqual(set(), user.get_all_permissions())


class CasUtilsTestCase(unittest.TestCase):

    def test_protocol(self):
        attrs = {'is_secure.return_value': True}
        request = unittest.mock.Mock(**attrs)
        self.assertEqual(protocol(request), 'https://')

        attrs = {'is_secure.return_value': False}
        request = unittest.mock.Mock(**attrs)
        self.assertEqual(protocol(request), 'http://')

    def test_host_url(self):
        attrs = {'is_secure.return_value': True,
                 'get_host.return_value': 'localhost:8000'}
        request = unittest.mock.Mock(**attrs)
        self.assertEqual(host_url(request), 'https://localhost:8000')

        path = '/login'
        self.assertEqual(host_url(request, path),
                         'https://localhost:8000/login')
