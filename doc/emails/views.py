from collections import OrderedDict

from vanilla import TemplateView

from doc.db.views import TripsYearMixin
from doc.permissions.views import DatabaseReadPermissionRequired
from doc.applications.models import GeneralApplication


def email_lists(trips_year):

    qs = GeneralApplication.objects.filter(trips_year=trips_year)

    def emails(qs):
        """ Return a list of applicant emails from GenApp qs """
        values = qs.values('applicant__email')
        return list(map(lambda x: x['applicant__email'], values))

    return OrderedDict([
        ('all applicants', emails(qs)),
        ('completed leader application', emails(
            GeneralApplication.objects.leader_applications(trips_year))),
        ('completed croo application', emails(
            GeneralApplication.objects.croo_applications(trips_year))),
        ('leaders', emails(qs.filter(
            status=GeneralApplication.LEADER))),
        ('leader waitlist', emails(
            qs.filter(status=GeneralApplication.LEADER_WAITLIST))),
        ('croo members', emails(
            qs.filter(status=GeneralApplication.CROO))),
        ('rejected applicants', emails(
            qs.filter(status=GeneralApplication.REJECTED))),
    ])


class EmailList(DatabaseReadPermissionRequired, TripsYearMixin, 
                 TemplateView):
    template_name = 'emails/emails.html'

    def get_context_data(self, **kwargs):
        context = super(EmailList, self).get_context_data(**kwargs)
        context['email_lists'] = email_lists(self.kwargs['trips_year'])
        return context
