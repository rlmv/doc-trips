from django.template import Library

register = Library()


@register.inclusion_tag('gear/_request.html')
def gear_request(req):
    return {
        'gear_request': req
    }
