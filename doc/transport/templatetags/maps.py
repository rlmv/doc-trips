from django.template import Library, loader, Context
from django.conf import settings

from doc.transport.maps import _split_stops

register = Library()

@register.simple_tag
def embed_map(stops):
    """
    Embed a google map in the page, showing directions
    along the passed stops. The stop[0] is the origin,
    stop[-1] the destination. Intermediate stops are 
    waypoints on the route.
    """
    orig, waypoints, dest = _split_stops(stops)
    return loader.get_template(
        'transport/maps/embed.html'
    ).render(Context({
        'orig': orig,
        'waypoints': waypoints,
        'dest': dest,
        'key': settings.GOOGLE_MAPS_BROWSER_KEY
    }))
