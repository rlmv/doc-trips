
from django import template
from django.utils.http import urlquote
from django.core.urlresolvers import reverse

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
