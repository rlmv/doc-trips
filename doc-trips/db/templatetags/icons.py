
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def ok_if_true(condition):
    """ If condition is true, insert an 'ok' tick mark. """

    if condition:
        html = '<div class="text-center"><span class="glyphicon glyphicon-ok"/></div>'
        return mark_safe(html)

    return ''

@register.filter
def checkmark_if_true(condition):
    """ If condition is true, show a checked box; otherwise, show empty box """
    
    if condition:
        html = '<span class="glyphicon glyphicon-check" aria-hidden="true"></span>' 
    else:
        html = '<span class="glyphicon glyphicon-unchecked" aria-hidden="true"></span>'
    return mark_safe(html)
    
