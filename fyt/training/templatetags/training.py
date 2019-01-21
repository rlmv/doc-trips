from django import template
from django.utils.safestring import mark_safe

from fyt.utils.templatetags.tooltips import tooltip_wrap


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
        text = '{}/{}'.format(session.registered.count(), session.DEFAULT_CAPACITY)

    return mark_safe(
        '<span class="label label-{} label-training-capacity"> {} </span>'.format(
            label, text
        )
    )


@register.filter
def training_label(volunteer):
    """
    Generate a label showing whether the volunteer has completed all
    trainings.

    Note that this takes a Volunteer instance, not an Attendee.
    """
    if volunteer.attendee.training_complete():
        label = 'success'
        text = 'Complete'
    else:
        label = 'warning'
        text = 'Incomplete'

    return mark_safe('<span class="label label-{}"> {} </span>'.format(label, text))


@register.filter
def first_aid_label(volunteer):
    """
    Generate a label showing whether the volunteer has completed all
    first aid requirements.

    Note that this takes a Volunteer instance, not an Attendee.
    """
    if volunteer.first_aid_complete:
        label = 'success'
        text = 'Complete'
    else:
        label = 'warning'
        text = 'Incomplete'

    tooltip = (
        'These are considered complete when a volunteer has a verified '
        'first aid certification and a verified CPR certification.'
    )

    return tooltip_wrap(
        '<span class="label label-{}"> {} </span>'.format(label, text), tooltip
    )
