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


@register.filter
def training_label(volunteer):
    """
    Generate a label showing whether the volunteer has completed all
    trainings and their first aid requirement.

    Note that this takes a Volunteer instance, not an Attendee.
    """
    attendee = volunteer.attendee
    if attendee.first_aid_complete() and attendee.training_complete():
        label = 'success'
        text = 'Complete'
    else:
        label = 'warning'
        text = 'Incomplete'

    return mark_safe('<span class="label label-{}"> {} </span>'.format(
            label, text))
