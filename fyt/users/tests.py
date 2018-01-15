from django.test.utils import override_settings
from django.urls import reverse
from model_mommy import mommy

from fyt.test import FytTestCase, vcr
from fyt.users.models import MAX_NETID_LENGTH, DartmouthUser


class UserManagerTestCase(FytTestCase):

    @vcr.use_cassette
    def test_create_user(self):
        netid = 'd123456z'
        name = 'Igor'

        user, ct = DartmouthUser.objects.get_or_create_by_netid(netid, name)
        self.assertTrue(ct)
        self.assertEqual(user.netid, netid)
        self.assertEqual(user.name, name)

        # Second retrieval: not created, name doesn't change
        user, ct = DartmouthUser.objects.get_or_create_by_netid(netid, 'Ogor')
        self.assertFalse(ct)
        self.assertEqual(user.netid, netid)
        self.assertEqual(user.name, name)

    @vcr.use_cassette
    def test_email_lookup_error_sets_blank_email(self):
        user = DartmouthUser.objects.create_user('junk_netid', 'name')
        self.assertEqual(user.email, '')

    def test_create_user_without_netid(self):
        name = 'name'
        email = 'email@email.org'

        user = DartmouthUser.objects.create_user_without_netid(name, email)
        self.assertEqual(user.name, name)
        self.assertEqual(user.netid, name)
        self.assertEqual(user.email, email)

        name = 'a' * (MAX_NETID_LENGTH + 1)  # One character too long

        user = DartmouthUser.objects.create_user_without_netid(name, email)
        self.assertEqual(user.name, name)
        self.assertEqual(user.netid, name[:20])
        self.assertEqual(user.email, email)


class NetIdFieldTestCase(FytTestCase):

    def test_lowercase_conversion(self):
        netid = 'D34898Z'
        user = mommy.make(DartmouthUser, netid=netid)
        self.assertEqual(user.netid, netid.lower())

    def test_lowercase_conversion_and_query(self):
        netid = 'D34898Z'
        user = mommy.make(DartmouthUser, netid=netid)
        self.assertEqual(user, DartmouthUser.objects.get(netid=netid))


class UserEmailMiddlewareTestCase(FytTestCase):

    def setUp(self):
        self.user = DartmouthUser.objects.create(
            netid='d34898z', name='test', email='')
        self.update_url = reverse('users:update_email')

    def test_user_with_no_email_must_manually_add_email(self):
        resp = self.app.get('/', user=self.user, status=302).follow()
        self.assertEqual(resp.request.path, self.update_url)
        resp.form['email'] = 'd34898z@test.com'
        resp = resp.form.submit().follow()
        # redirects back to original location
        self.assertEqual(resp.request.path, '/')
        # and updates email
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'd34898z@test.com')

    def test_update_email_does_not_need_next_in_querystring(self):
        resp = self.app.get(self.update_url, user=self.user)
        resp.form['email'] = 'd34898z@test.com'
        resp = resp.form.submit().follow()
        self.assertEqual(resp.request.path, '/')
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'd34898z@test.com')

    @override_settings(CAS_LOGOUT_COMPLETELY=False)
    def test_do_not_ask_for_email_when_logging_out(self):
        resp = self.app.get(reverse('users:logout'), user=self.user).follow()
        self.assertFalse(resp.request.path.startswith(self.update_url))


class UserUrlsTestCase(FytTestCase):

    def test_unauthorized_user_is_redirected_to_login(self):
        target_url = reverse('applications:portal')
        resp = self.app.get(target_url, status=302)
        login_url = reverse('users:login') + '?next=' + target_url
        self.assertEqual(resp.url, login_url)
