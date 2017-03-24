
from django.conf import settings
from django.shortcuts import redirect


def CanonicalHostMiddleware(get_response):
    """
    Redirect requests to the doc-trips.herokuapp.com url to doctrips.org.
    """
    def middleware(request):

        if request.get_host() == settings.HEROKU_HOST:
            url = '{}://{}{}'.format(
                request.scheme,
                settings.CANONICAL_HOST,
                request.get_full_path()
            )
            return redirect(url, permanent=True)

        return get_response(request)

    return middleware
