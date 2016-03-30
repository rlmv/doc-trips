
from urllib.parse import urljoin, urlencode

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import auth
from django.shortcuts import render

from fyt.dartdm.lookup import EmailLookupException


__all__ = ['login', 'logout']


def protocol(request):
    return ('http://', 'https://')[request.is_secure()]


def host_url(request, path=None):
    """Extract the prefix (HTTP scheme and host) of the request URL.

    ``path`` is an optional path on the host server to apppend to the url."""
    if path is None:
        path = ''
    return protocol(request) + request.get_host() + path


def _service_url(request, redirect_to=None):
    """Generates application service URL for CAS"""

    service = host_url(request, request.path)
    if redirect_to:
        if '?' in service:
            service += '&'
        else:
            service += '?'
        service += urlencode({REDIRECT_FIELD_NAME: redirect_to})
    return service


def _redirect_url(request):
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer"""

    next = request.GET.get(REDIRECT_FIELD_NAME)
    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)

        if next.startswith(host_url(request)):
            next = next[len(host_url(request)):]
    return next


def _cas_login_url(service):
    """Return CAS login url. """

    qs = urlencode({'service': service})
    return urljoin(settings.CAS_SERVER_URL, 'login') + '?' + qs


def _cas_logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        url += '?' + urlencode({'url': host_url(request, next_page)})
    return url


def login(request, next_page=None):
    """Forwards to CAS login URL or verifies CAS ticket"""

    if not next_page:
        next_page = _redirect_url(request)

    if request.user.is_authenticated():
        return HttpResponseRedirect(next_page)

    service = _service_url(request, next_page)
    ticket = request.GET.get('ticket')

    if ticket:

        # Catch exception thrown by dartdm.lookup.email_lookup
        try:
            user = auth.authenticate(ticket=ticket, service=service)
        except EmailLookupException as e:
            return render(
                request, 'webauth/email_lookup_error.html', {'exception': e})

        if user is not None:
            # Has ticket, logs in fine
            auth.login(request, user)
            return HttpResponseRedirect(next_page)
        else:
            error = ('<h1>Forbidden</h1>'
                     '<p>Login failed. Please try logging in again.</p>')
            return HttpResponseForbidden(error)
    else:
        return HttpResponseRedirect(_cas_login_url(service))


def logout(request, next_page=None):
    """Redirects to CAS logout page"""

    from django.contrib.auth import logout
    logout(request)

    if not next_page:
        next_page = _redirect_url(request)

    if settings.CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_cas_logout_url(request, next_page))
    else:
        return HttpResponseRedirect(next_page)
