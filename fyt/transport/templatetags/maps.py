from django.conf import settings
from django.template import Library, loader

from fyt.transport.maps import MapError, _split_stops


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

    return loader.get_template('transport/maps/embed.html').render(
        {
            'orig': orig,
            'waypoints': waypoints,
            'dest': dest,
            'key': settings.GOOGLE_MAPS_BROWSER_KEY,
        }
    )


@register.inclusion_tag('transport/maps/directions.html')
def directions(bus):
    """
    Given an internal bus, display directions or MapError.
    """
    try:
        return {
            # TODO: refactor to use bus.directions()
            'directions': bus.update_stop_times(),
            'stop_template': 'transport/maps/_internal_stop.html',
        }
    except MapError as exc:
        return {'error': exc}


@register.inclusion_tag('transport/maps/directions.html')
def directions_to_hanover(bus):
    """
    Directions for an external bus to hanover.
    """
    try:
        return {
            'directions': bus.directions_to_hanover(),
            'stop_template': 'transport/maps/_external_stop.html',
        }
    except MapError as exc:
        return {'error': exc}


@register.inclusion_tag('transport/maps/directions.html')
def directions_from_hanover(bus):
    """
    Directions for an external bus from hanover.
    """
    try:
        return {
            'directions': bus.directions_from_hanover(),
            'stop_template': 'transport/maps/_external_stop.html',
        }
    except MapError as exc:
        return {'error': exc}


@register.inclusion_tag('transport/maps/_trips_with_counts.html')
def trips_with_counts(trips):
    """
    Checklist of trips with size of trips.
    """
    return {'trips': trips}


def _decdeg2dms(dd):
    """
    Convert decimal degrees to degrees-minutes-secondes.
    """
    negative = dd < 0
    dd = abs(dd)
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    return (negative, degrees, minutes, seconds)


def _fmt_side(dec, direction_chars):
    """
    Format one part of a DMS coordinate.
    """
    negative, degrees, minutes, seconds = _decdeg2dms(dec)
    if negative:
        direction = direction_chars[0]
    else:
        direction = direction_chars[1]

    return """{:.0f}\u00B0{:02.0f}'{:04.1f}"{}""".format(
        degrees, minutes, seconds, direction
    )


@register.filter
def lat_lng_dms(lat_lng):
    """
    Temlate filter to convert decimal coordinates to DMS.
    """
    lat, lng = lat_lng.split(',')
    lat = float(lat.strip())
    lng = float(lng.strip())

    return '{} {}'.format(_fmt_side(lat, ['S', 'N']), _fmt_side(lng, ['W', 'E']))
