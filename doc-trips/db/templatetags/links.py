
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def edit_link(object):
    """ Return an html link to the update view for object 

    TODO: move html into the template itself? """
    html = '<a href="{}">edit</a>'.format(object.get_update_url())
    return mark_safe(html)
