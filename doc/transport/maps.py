import json

import googlemaps
from django.conf import settings 

from doc.transport.models import Stop

"""
Interface with the Google maps API
"""

TIMEOUT = 10  # -> settings

class MapError(Exception):
    pass

def get_hanover():
    return Stop(name='Hanover, NH', address='Hanover, NH')

def get_lodge():
    return Stop(name='The Moosilauke Ravine Lodge', address='43.977253,-71.8154831')


def get_directions(stops):

    addrs = list(map(lambda x: x.address, stops))

    orig = addrs[0]
    dest = addrs[-1]
    waypoints = addrs[1:-1]
    
    if len(waypoints) > 8:
        # TODO: recurse
        raise MapError('Too many waypoints: %s' % waypoints)
        
    client = googlemaps.Client(
        key=settings.GOOGLE_MAPS_KEY,
        timeout=TIMEOUT
    )

    try:
        resp = client.directions(
            origin=orig, destination=dest,
            waypoints=waypoints
        )
        if len(resp) != 1:
            raise MapError('Expecting one route')
        if resp[0]['waypoint_order'] != list(range(len(waypoints))):
            raise MapError('Waypoints out of order')
        
        return _integrate_stops(resp[0], stops)

    except googlemaps.exceptions.TransportError as exc:
        raise MapError(exc)


def _integrate_stops(directions, stops):
    """
    Given a google maps route, add a start_stop
    and end_stop object to each leg.

    The passed stops must be the stops used to generate 
    the directions. This only works if waypoints are not
    optimized.
    """
    if len(stops) != len(directions['legs']) + 1:
        raise MapError('mismatched stops and legs')

    for i, leg in enumerate(directions['legs']):
        leg['start_stop'] = stops[i]
        leg['end_stop'] = stops[i + 1]
        
    return directions
