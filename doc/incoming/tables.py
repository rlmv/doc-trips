import django_tables2 as tables

from doc.db.templatetags.links import detail_link, edit_link


class RegistrationTable(tables.Table):

    class Meta:
        attrs = {
            "class": "table table-condensed"  # bootstrap
        }

    user = tables.Column(
        verbose_name='Registration'
    )
    trippee = tables.Column(
        verbose_name='Incoming Student Data'
    )
    edit_link = tables.Column(
        verbose_name=' ', accessor='user'
    )

    def render_user(self, record):
        return detail_link(record)

    def render_trippee(self, value):
        return detail_link(value)

    def render_edit_link(self, record):
        return edit_link(record)
