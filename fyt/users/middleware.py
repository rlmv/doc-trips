from urllib.parse import urlencode

from django.contrib import auth
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class UserEmailRequiredMiddleware(MiddlewareMixin):
    """
    If an authenticated user does not have an email set,
    have them to enter it manually.

    A user will have a blank email if
    :meth:`~fyt.users.models.DartmouthUserManager.create_user`
    fails to lookup the email.
    """

    def process_request(self, request):
        update_url = reverse('users:update_email')

        if request.path == update_url:
            # avoid redirect loop
            return None

        if request.path == reverse('users:logout'):
            # allow people to logout without updating email
            return None

        if request.user.is_authenticated and not request.user.email:
            params = urlencode({auth.REDIRECT_FIELD_NAME: request.get_full_path()})
            return HttpResponseRedirect(update_url + '?' + params)
