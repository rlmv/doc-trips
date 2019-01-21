from django.template import Library


register = Library()


@register.inclusion_tag('gear/_request.html')
def gear_request(req):
    return {'gear_request': req}


@register.inclusion_tag('gear/_request_public.html')
def gear_request_portal(req):
    """For leader and trippee portal."""
    return {'gear_request': req}
