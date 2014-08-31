
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def edit_link(db_object, text=None):
    """ Insert the html link to edit db_object """
    if text is None:
        text = 'edit'
    html = '<a href="{}">{}</a>'.format(db_object.get_update_url(), text)
    return mark_safe(html)

@register.filter
def delete_link(db_object, text=None):
    """ Insert html link to delete db_object """
    if text is None:
        text = 'delete'
    html = '<a href="{}">{}</a>'.format(db_object.get_delete_url(), text)
    return mark_safe(html)

@register.filter
def absolute_link(db_object, text=None):
    if text is None:
        text = str(db_object)
    html = '<a href="{}">{}</a>'.format(db_object.get_absolute_url(), text)
    return mark_safe(html)

    
    
