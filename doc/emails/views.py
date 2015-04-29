from collections import OrderedDict

from vanilla import TemplateView

from doc.db.views import TripsYearMixin
from doc.permissions.views import DatabaseReadPermissionRequired
from doc.applications.models import GeneralApplication
from doc.trips.models import TripType


def email_lists(trips_year):

    qs = GeneralApplication.objects.filter(trips_year=trips_year)

    def emails(qs):
        """ Return a list of applicant emails from GenApp qs """
        values = qs.values('applicant__email')
        return list(map(lambda x: x['applicant__email'], values))

    email_list = [
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
    ]

    leaders = qs.filter(status=GeneralApplication.LEADER)
    triptypes = TripType.objects.filter(trips_year=trips_year)
    for triptype in triptypes:
        email_list.append(
            ('%s leaders' % triptype,
             emails(leaders.filter(assigned_trip__template__triptype=triptype)))
        )

    return OrderedDict(email_list)


class EmailList(DatabaseReadPermissionRequired, TripsYearMixin, 
                 TemplateView):
    template_name = 'emails/emails.html'

    def get_context_data(self, **kwargs):
        context = super(EmailList, self).get_context_data(**kwargs)
        context['email_lists'] = email_lists(self.kwargs['trips_year'])
        return context
