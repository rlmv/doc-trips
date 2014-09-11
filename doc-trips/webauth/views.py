# -*- coding: utf-8 -*-

"""CAS login/logout replacement views"""
from datetime import datetime
# from urllib import urlencode
from urllib.parse import urljoin, urlencode

from operator import itemgetter

from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

from django_cas.models import SessionServiceTicket

__all__ = ['login', 'logout']


def _service_url(request, redirect_to=None, gateway=False):
    """Generates application service URL for CAS"""

    protocol = ('http://', 'https://')[request.is_secure()]
    host = request.get_host()
    prefix = (('http://', 'https://')[request.is_secure()] + host)
    service = protocol + host + request.path
    if redirect_to:
        if '?' in service:
            service += '&'
        else:
            service += '?'
        service += urlencode({REDIRECT_FIELD_NAME: redirect_to})
    return service


def _redirect_url(request):
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.
    """

    next = request.GET.get(REDIRECT_FIELD_NAME)
    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)

        host = request.get_host()
        prefix = (('http://', 'https://')[request.is_secure()] + host)
        if next.startswith(prefix):
            next = next[len(prefix):]
    return next


def cas_login_url(service):
    """ Return CAS login url. """

    params = {'service': service}
    qs = urlencode(params)
    return urljoin(settings.CAS_SERVER_URL, 'login') + '?' + qs


def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urlencode({'url': protocol + host + next_page})
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

        from django.contrib import auth
        user = auth.authenticate(ticket=ticket, service=service)

        if user is not None:
            #Has ticket, logs in fine
            auth.login(request, user)
            return HttpResponseRedirect(next_page)
        else:
             error = ('<h1>Forbidden</h1><p>Login failed. '
                      'Please try logging in again.</p>')
             return HttpResponseForbidden(error)
    else:
        return HttpResponseRedirect(cas_login_url(service))


def logout(request, next_page=None):
    """Redirects to CAS logout page"""

    from django.contrib.auth import logout
    logout(request)

    if not next_page:
        next_page = _redirect_url(request)
    if settings.CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_logout_url(request, next_page))
    else:
        return HttpResponseRedirect(next_page)

