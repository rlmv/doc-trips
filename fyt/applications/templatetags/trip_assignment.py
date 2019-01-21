from django.template import Library


register = Library()


@register.inclusion_tag('applications/_leader_assignment.html')
def trip_assignment(trip, content):
    return {'trip': trip, 'content': content}
