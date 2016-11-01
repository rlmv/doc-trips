
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponseForbidden

from fyt.webauth.views import login as cas_login, logout as cas_logout


class WebAuthMiddleware(object):
    """Middleware that allows CAS authentication on admin pages"""

    def process_request(self, request):
        """Checks that the authentication middleware is installed"""

        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        assert hasattr(request, 'user'), error

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """
        if view_func == auth.views.login:
            return cas_login(request, *view_args, **view_kwargs)
        elif view_func == auth.views.logout:
            return cas_logout(request, *view_args, **view_kwargs)

        if not view_func.__module__.startswith('django.contrib.admin.'):
            # Not admin? then we don't care. Pass along the request.
            return None

        if not request.user.is_authenticated:
            login_url = settings.LOGIN_URL + '?' + urlencode({
                auth.REDIRECT_FIELD_NAME: request.get_full_path()})
            return HttpResponseRedirect(login_url)

        if request.user.is_staff:
            return None

        error = ('<h1>Forbidden</h1>'
                 '<p>You do not have staff privileges.</p>')
        return HttpResponseForbidden(error)
