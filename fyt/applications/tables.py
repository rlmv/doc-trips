import django_tables2 as tables
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from fyt.db.templatetags.links import detail_link, make_link, edit_link
from fyt.utils.templatetags.icons import ok_if_true


def tooltip_wrap(target, tooltip):
    """
    Wrap a string with a Bootstrap tooltip
    """
    return mark_safe(
        '<span data-toggle="tooltip" data-placement="top" title="{}"> {} </span>'.format(tooltip, target)
    )


class TrainingColumn(tables.Column):
    """
    Column with a tooltip
    """
    def __init__(self, verbose_name, tooltip, *args, **kwargs):
        self.tooltip = tooltip
        verbose_name = tooltip_wrap(verbose_name, self.tooltip)
        super(TrainingColumn, self).__init__(verbose_name, *args, **kwargs)

    def render(self, value):
        return tooltip_wrap(value.strftime("%m/%d").lstrip('0'), self.tooltip)


class ApplicationTable(tables.Table):

    applicant = tables.Column(
        verbose_name='Applications'
    )
    netid = tables.Column(
        verbose_name='NetId', accessor='applicant.netid'
    )
    status = tables.Column(
        verbose_name='Status'
    )
    avg_leader_grade = tables.Column(
        verbose_name='Leader score', order_by=('-avg_leader_grade')
    )
    avg_croo_grade = tables.Column(
        verbose_name='Croo score', order_by=('-avg_croo_grade')
    )
    leader_application = tables.Column(
        verbose_name='Leader app',
        accessor='leader_application_complete', orderable=False
    )
    croo_application = tables.Column(
        verbose_name='Croo app',
        accessor='croo_application_complete', orderable=False
    )
    community_building = TrainingColumn(
        verbose_name='CB', tooltip="Community Building"
    )
    risk_management = TrainingColumn(
        verbose_name='RM', tooltip="Risk Management"
    )
    wilderness_skills = TrainingColumn(
        verbose_name='WS', tooltip="Wilderness Skills"
    )
    croo_training = TrainingColumn(
        verbose_name='CT', tooltip="Croo Training"
    )
    first_aid = tables.Column(
        verbose_name='med cert',
        accessor='get_first_aid_cert', orderable=False
    )

    class Meta:
        attrs = {
            "class": "table table-condensed"  # bootstrap class
        }

    def render_applicant(self, record):
        return detail_link(record)

    def render_status(self, record):
        kwargs = {'pk': record.pk, 'trips_year': record.trips_year_id}
        url = reverse('db:update_application_status', kwargs=kwargs)
        return make_link(url, record.get_status_display())

    def render_avg_leader_grade(self, value):
        return "%.1f" % value

    def render_avg_croo_grade(self, value):
        return "%.1f" % value

    def render_leader_application(self, value):
        return ok_if_true(value)

    def render_croo_application(self, value):
        return ok_if_true(value)

    def render_first_aid(self, value):
        if len(value) > 6:
            return tooltip_wrap(value[:6], value)
        return value

