from django.contrib.auth import get_user_model

from test.fixtures import TripsYearTestCase

class GroupPermissionsTest(TripsYearTestCase):

    def test_group_permissions_work_with_custom_backend(self):
        # None of the permissions worked when the backend 
        # did not inherit from ModelBackend
        
        # the director group SHOULD have a number of permissions 
        user = self.mock_director()
        self.assertNotEqual(set(), user.get_all_permissions())
        
        
