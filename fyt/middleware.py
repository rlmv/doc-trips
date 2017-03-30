
from django.conf import settings
from django.shortcuts import redirect


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
