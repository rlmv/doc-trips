import django_tables2 as tables
from django.core.urlresolvers import reverse

from doc.db.templatetags.links import detail_link, make_link, edit_link
from doc.utils.templatetags.icons import ok_if_true


class ApplicationTable(tables.Table):
    
    applicant = tables.Column(
        verbose_name='Applications'
    )
    status = tables.Column(
        verbose_name='Status'
    )
    avg_leader_grade = tables.Column(
        verbose_name='Leader score', order_by='-avg_leader_grade'
    )
    avg_croo_grade = tables.Column(
        verbose_name='Croo score',  order_by='-avg_croo_grade'
    )
    leader_application = tables.Column(
        accessor='leader_application_complete', orderable=False
    )
    croo_application = tables.Column(
        accessor='croo_application_complete', orderable=False
    )
    view_link = tables.Column(
        verbose_name=' ', empty_values=(), orderable=False
    )
    edit_link = tables.Column(
        verbose_name=' ', empty_values=(), orderable=False)

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

    def render_leader_score(self, value):
        return "%.1f" % value

    def render_croo_score(self, value):
        return "%.1f" % value

    def render_leader_application(self, value):
        return ok_if_true(value)

    def render_croo_application(self, value):
        return ok_if_true(value)

    def render_view_link(self, record):
        return detail_link(record, 'view')

    def render_edit_link(self, record):
        return edit_link(record, 'edit')
