import django_tables2 as tables
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from fyt.db.templatetags.links import detail_link, make_link
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
        super().__init__(verbose_name, *args, **kwargs)

    def render(self, value):
        return tooltip_wrap(value.strftime("%m/%d").lstrip('0'), self.tooltip)


class _ApplicationTable(tables.Table):

    applicant = tables.Column(
        verbose_name='Applications'
    )
    netid = tables.Column(
        verbose_name='NetId', accessor='applicant.netid'
    )
    status = tables.Column(
        verbose_name='Status'
    )
    gender = tables.Column(
        verbose_name='Gender'
    )
    avg_score = tables.Column(
        verbose_name='Score', order_by='-norm_avg_score'
    )
    leader_application = tables.Column(
        verbose_name='Leader app',
        accessor='leader_application_complete', orderable=False
    )
    croo_application = tables.Column(
        verbose_name='Croo app',
        accessor='croo_application_complete', orderable=False
    )

    class Meta:
        attrs = {
            "class": "table table-condensed"  # bootstrap class
        }

    def render_applicant(self, record):
        return detail_link(record)

    def render_status(self, record):
        kwargs = {'pk': record.pk, 'trips_year': record.trips_year_id}
        url = reverse('db:volunteer:update_status', kwargs=kwargs)
        return make_link(url, record.get_status_display())

    def render_avg_score(self, value):
        return "%.1f" % value

    def render_leader_application(self, value):
        return ok_if_true(value)

    def render_croo_application(self, value):
        return ok_if_true(value)


def ApplicationTable(qs, request):
    """Configure and return an ``_ApplicationTable`` for this request."""
    table = _ApplicationTable(qs)
    tables.RequestConfig(request, paginate=False).configure(table)
    return table
