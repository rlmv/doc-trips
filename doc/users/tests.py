
from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

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


class NetIdFieldTestCase(TestCase):
    
    def test_lowercase_conversion(self):
        netid = 'D34898Z'
        user = mommy.make(DartmouthUser, netid=netid)
        self.assertEqual(user.netid, netid.lower())

    def test_lowercase_conversion_and_query(self):
        netid = 'D34898Z'
        user = mommy.make(DartmouthUser, netid=netid)
        self.assertEqual(user, DartmouthUser.objects.get(netid=netid))
