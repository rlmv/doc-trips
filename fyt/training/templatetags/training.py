from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def capacity_label(session):
    """
    Generate a label showing whether the session is full, or it's capacity.
    """
    if session.full():
        label = 'danger'
        text = 'full'
    else:
        label = 'success'
        text = '{}/{}'.format(session.registered.count(),
                              session.DEFAULT_CAPACITY)

    return mark_safe(
        '<span class="label label-{} label-training-capacity"> {} </span>'.format(label, text))
