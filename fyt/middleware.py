import logging

from django.conf import settings
from django.shortcuts import redirect


log = logging.getLogger(__name__)


def CanonicalHostMiddleware(get_response):
    """
    Redirect requests to the doc-trips.herokuapp.com url to doctrips.org.
    """
    def middleware(request):

        # TODO: remove -> SecurityMiddleware
        if settings.PRODUCTION and request.method == 'GET' and request.scheme == 'http':
            url = 'https://{}{}'.format(
                request.get_host(),
                request.get_full_path()
            )
            return redirect(url, permanent=True)

        if request.get_host() == settings.HEROKU_HOST:
            url = '{}://{}{}'.format(
                request.scheme,
                settings.CANONICAL_HOST,
                request.get_full_path()
            )
            return redirect(url, permanent=True)

        return get_response(request)

    return middleware


def UserLoggerMiddleware(get_response):
    """
    Log the user and IP address to facilitate Papertrail debugging.
    """
    def middleware(request):

        if settings.PRODUCTION:
            header = 'HTTP_X_FORWARDED_FOR'
            if request.META.get(header, None):
                # Heroku sets the remote host last
                ip = request.META[header].split(',')[-1].strip()
            else:
                ip = request.META['REMOTE_ADDR']

            log.info("ip={} user={}".format(ip, request.user))

        return get_response(request)

    return middleware
