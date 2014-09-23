
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def checkmark_if_true(condition):
    """ If condition is true, insert an 'ok' tick mark. """

    if condition:
        html = '<div class="text-center"><span class="glyphicon glyphicon-ok"/></div>'
        return mark_safe(html)

    return ''
    
    
    
