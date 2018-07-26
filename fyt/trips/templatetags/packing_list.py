from django import template

register = template.Library()

@register.inclusion_tag('trips/_packing_list.html')
def packing_list(triptype, link_to_request_form=True):
    return {
        'triptype': triptype,
        'link_to_request_form': link_to_request_form}
