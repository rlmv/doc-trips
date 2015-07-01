
import googlemaps
from django.conf import settings 

from doc.transport.models import Stop

"""
Interface with the Google maps API
"""

TIMEOUT = 1  # -> settings

class MapsError(Exception):
    pass

def get_hanover():
    return Stop(name='Hanover, NH', address='Hanover, NH')

def get_lodge():
    return Stop(name='Lodge', address='1 Ravine Lodge Rd, Woodstock NH')


def get_directions(stops):

    stops = list(map(lambda x: x.address, stops))

    orig = stops[0]
    dest = stops[-1]
    waypoints = stops[1:-1]
    
    if len(waypoints) > 8:
        # TODO: recurse
        raise MapsError('Too many waypoints: %s' % waypoints)
        
    client = googlemaps.Client(
        key=settings.GOOGLE_MAPS_KEY,
        timeout=TIMEOUT
    )

    client.directions(
        origin=orig, destination=dest,
        waypoints=waypoints, optimize_waypoints=True
    )
