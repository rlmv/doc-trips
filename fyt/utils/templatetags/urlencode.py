from urllib.parse import urlencode as _urlencode

from django import template

register = template.Library()


@register.simple_tag
def urlencode(**kwargs):
    return _urlencode(kwargs)
