from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def ok_if_true(condition):
    """ If condition is true, insert an 'ok' tick mark. """

    if condition:
        html = '<i class="fa fa-check"></i>'
        return mark_safe(html)
    return ''


@register.filter
def checkmark_if_true(condition):
    """ If condition is true, show a checked box; otherwise, show empty box """

    if condition:
        html = '<i class="fa fa-check-square-o"></i>'
    else:
        html = '<i class="fa fa-square-o"></i>'
    return mark_safe(html)


@register.simple_tag
def warning_sign():
    """Warning exclamation mark."""
    return mark_safe('<i class="fa fa-exclamation fa-fw text-bright-danger"></i>')
