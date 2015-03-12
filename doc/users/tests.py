
from unittest.mock import patch

from django.test import TestCase

from doc.users.models import DartmouthUser


def lookup_email(*args, **kwargs):
    return 'email'
    
@patch('doc.users.models.lookup_email', new=lookup_email)
class UserManagerTestCase(TestCase):

    def test_create_user_without_did(self):
        
        netid = 'd123456z'
        name = 'Igor'
        
        user, ct = DartmouthUser.objects.get_or_create_by_netid(netid, name)
        self.assertTrue(ct)
        self.assertEqual(user.netid, netid)
        self.assertEqual(user.name, name)
        self.assertEqual(user.did, '')
       
    def test_create_user_then_add_did(self):
        
        netid = 'd123456z'
        name = 'Igor'
        user, ct = DartmouthUser.objects.get_or_create_by_netid(netid, name)
        
        DID = 'destiny'
        user, ct = DartmouthUser.objects.get_or_create_by_netid(netid, name, did=DID)
        self.assertFalse(ct)
        self.assertEqual(user.netid, netid)
        self.assertEqual(user.name, name)
        self.assertEqual(user.did, DID)
        
        
