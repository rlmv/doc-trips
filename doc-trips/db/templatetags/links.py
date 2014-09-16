
from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from db.models import TripsYear
from db.urls import get_update_url, get_delete_url, get_create_url

register = template.Library()

def _make_link(url, text):
    """ Format a link. """
    html = '<a href="{}">{}</a>'.format(url, text)
    return mark_safe(html)


@register.filter
def edit_link(db_object, text=None):
    """ Insert html link to edit db_object. """
    if text is None:
        text = 'edit'
    return _make_link(get_update_url(db_object), text)

        
@register.filter
def delete_link(db_object, text=None):
    """ Insert html link to delete db_object. """
    if text is None:
        text = 'delete'
    return _make_link(get_delete_url(db_object), text)


@register.simple_tag
def create_url(model, trips_year_str):
    """ Give the create url for the given model and trips_year """

    trips_year = TripsYear.objects.get(pk=trips_year_str)

    return get_create_url(model, trips_year)
    

@register.filter
def absolute_link(db_object, text=None):

    if text is None:
        text = str(db_object)
    # TODO: use detail view here, if we ever implement it
    return _make_link(get_update_url(db_object), text)
