import googlemaps
from django.conf import settings
from googlemaps.exceptions import ApiError, TransportError


"""
Interface with the Google maps API
"""

TIMEOUT = 10  # -> settings
MAX_WAYPOINTS = 8  # imposed by Google Maps


class MapError(Exception):
    pass


def _split_stops(stops):
    """
    Given an ordered route of stops, return a tuple
    (origin, waypoints, destion) of address or geo
    coordinates.
    """
    addrs = [x.location for x in stops]
    return (addrs[0], addrs[1:-1], addrs[-1])


def get_directions(stops):
    """
    Do a Google maps directions lookup.

    Returns a maps json response, with a start_stop
    and end_stop Stop objects added to each leg.

    TODO: just return the 'legs' value
    """
    if len(stops) < 2:
        raise MapError('Only one stop provided')

    orig, waypoints, dest = _split_stops(stops)

    if len(waypoints) > MAX_WAYPOINTS:
        d1 = get_directions(stops[:MAX_WAYPOINTS])
        d2 = get_directions(stops[MAX_WAYPOINTS - 1:])

        # sanity check
        if d1['legs'][-1]['end_stop'] != d2['legs'][0]['start_stop']:
            raise MapError('mismatched end and start stops on recursion')

        return {'legs': d1['legs'] + d2['legs']}

    client = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY, timeout=TIMEOUT)

    try:
        resp = client.directions(
            origin=orig, destination=dest, waypoints=waypoints
        )
        if len(resp) != 1:
            raise MapError('Expecting one route')
        if resp[0]['waypoint_order'] != list(range(len(waypoints))):
            raise MapError('Waypoints out of order')

        return _integrate_stops(resp[0], stops)

    except (TransportError, ApiError) as exc:
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
