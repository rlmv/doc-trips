
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def edit_link(db_object):
    """ Insert the html link to edit db_object """

    html = '<a href="{}">edit</a>'.format(db_object.get_update_url())
    return mark_safe(html)

@register.filter
def delete_link(db_object):
    
    html = '<a href="{}">delete</a>'.format(db_object.get_delete_url())
    return mark_safe(html)
    
    
