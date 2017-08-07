import googlemaps
from django.conf import settings
from googlemaps.exceptions import ApiError, TransportError
from datetime import timedelta


"""
Interface with the Google Maps Directions API

See https://developers.google.com/maps/documentation/directions/intro
for more information about the format of the response object.
"""

TIMEOUT = 10
MAX_WAYPOINTS = 23  # imposed by Google Maps


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

    # TODO: now that MAX_WAYPOINTS is 23, can we remove this?
    # Is there ever a route with 23 stops?
    if len(waypoints) > MAX_WAYPOINTS:
        d1 = get_directions(stops[:MAX_WAYPOINTS])
        d2 = get_directions(stops[MAX_WAYPOINTS - 1:])

        # Sanity check
        if d1.legs[-1].end_stop != d2.legs[0].start_stop:
            raise MapError('mismatched end and start stops on recursion')

        return Directions({'legs': d1.legs + d2.legs}, stops)

    client = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY, timeout=TIMEOUT)

    try:
        resp = client.directions(
            origin=orig, destination=dest, waypoints=waypoints)
    except (TransportError, ApiError) as exc:
        raise MapError(exc)

    if len(resp) != 1:
        raise MapError('Expecting one route')
    if resp[0]['waypoint_order'] != list(range(len(waypoints))):
        raise MapError('Waypoints out of order')

    return Directions(resp[0], stops)


class Directions:
    """
    Wrapper for the Google Maps direction response.

    The passed stops must be the stops used to generate the directions.
    """
    def __init__(self, raw_json, stops):
        self.raw = raw_json
        self.stops = stops

        if len(stops) != len(raw_json['legs']) + 1:
            raise MapError('mismatched stops and legs')

        self.legs = [Leg(leg, stops[i], stops[i+1])
                     for i, leg in enumerate(raw_json['legs'])]


class Leg:
    """
    Wrapper for a leg of a route.

    Each leg has a `start_stop` and `end_stop` attribute, corresponding
    to the Stop objects on either end of the leg.
    """
    def __init__(self, raw_json, start_stop, end_stop):
        self.raw = raw_json
        self.start_stop = start_stop
        self.end_stop = end_stop
        self.start_time = None
        self.end_time = None

    @property
    def duration(self):
        return timedelta(seconds=self.raw['duration']['value'])

    @property
    def steps(self):
        return self.raw['steps']
