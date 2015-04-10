from django.conf.urls import url

from doc.reports.views import VolunteerCSV

urlpatterns = [
    url(r'^export/$', VolunteerCSV.as_view(), name='application_csv'),
]
