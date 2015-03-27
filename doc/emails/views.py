
from vanilla import TemplateView

from doc.db.views import TripsYearMixin
from doc.permissions.views import DatabaseReadPermissionRequired
from doc.applications.models import GeneralApplication


def email_lists(trips_year):

    def emails(**filter_kwargs):
        values = (
            GeneralApplication.objects
            .filter(trips_year=trips_year)
            .filter(**filter_kwargs)
            .values('applicant__email')
        )
        return list(map(lambda x: x['applicant__email'], values))

    return {
        'all applicants': emails(),
        'leaders': emails(status=GeneralApplication.LEADER),
        'leader waitlist': emails(status=GeneralApplication.LEADER_WAITLIST),
        'croos': emails(status=GeneralApplication.CROO),
        'rejected': emails(status=GeneralApplication.REJECTED),
    }


class EmailList(DatabaseReadPermissionRequired, TripsYearMixin, 
                 TemplateView):
    template_name = 'emails/emails.html'

    def get_context_data(self, **kwargs):
        context = super(EmailList, self).get_context_data(**kwargs)
        context['email_lists'] = email_lists(self.kwargs['trips_year'])
        return context
