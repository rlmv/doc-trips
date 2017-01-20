
from django import template
from django.core.urlresolvers import reverse
from django.utils.http import urlquote


register = template.Library()


@register.simple_tag
def new_raid_url(trips_year, **kwargs):
    """
    Url to create a new raid, with kwargs added to 
    url querystring and encoded.
    """
    url = reverse('db:raids:create', kwargs={'trips_year': trips_year})

    if kwargs:
        url += '?' + '&'.join(['%s=%s' % (k, v) for (k, v) in kwargs.items()])
    return url


@register.inclusion_tag('raids/trip_modal.html')
def trip_modal(trip, link_text=None):
    if link_text is None:
        link_text = str(trip)
    return {'trip': trip, 'link_text': link_text}


@register.inclusion_tag('raids/campsite_modal.html')
def campsite_modal(campsite):
    return {'campsite': campsite}
