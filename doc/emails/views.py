
from vanilla import TemplateView

from doc.db.views import TripsYearMixin
from doc.permissions.views import DatabaseReadPermissionRequired


class EmailList(DatabaseReadPermissionRequired, TripsYearMixin, 
                 TemplateView):
    template_name = 'emails/emails.html'
