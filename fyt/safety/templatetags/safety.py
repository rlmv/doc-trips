from django import template
from django.utils.safestring import mark_safe

from fyt.safety.models import Incident

register = template.Library()


@register.filter
def status_label(incident):
    """
    Show a color-coded status label for an Incident.
    """
    opts = {
        Incident.OPEN: 'warning',
        Incident.RESOLVED: 'success'
    }
    return mark_safe(
        '<span class="label label-%s"> %s </span>' % (
            opts[incident.status], incident.get_status_display().upper()
        ))
