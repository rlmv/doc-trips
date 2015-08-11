
from django import template

register = template.Library()

@register.inclusion_tag('trips/_packet.html')
def leader_packet(trip):
    return {'trip': trip}


@register.inclusion_tag('trips/_medical.html')
def medical_packet(trip):
    return {'trip': trip}
