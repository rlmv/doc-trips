

from django.conf.urls import patterns, url, include
from croos.views import CrooApplicationView, CrooApplicationCreate, CreateCrooApplication, RedirectToNextGradableCrooApplication, GradeCrooApplication, NoCrooApplicationsLeftToGrade

urlpatterns = patterns('', 
    url(r'^apply/$', CrooApplicationCreate.as_view(), name='apply'),
    url(r'^apply/edit$', CrooApplicationView.as_view(), name='edit_application'),
    url(r'^createapplication/$', CreateCrooApplication.as_view(), name='create_application'),                   
    url(r'^grade/$', RedirectToNextGradableCrooApplication.as_view(), name='grade_next'),
    url(r'^grade/(?P<pk>[0-9]+)$', GradeCrooApplication.as_view(), name='grade'),
    url(r'^grade/none/$', NoCrooApplicationsLeftToGrade.as_view(), name='no_applications'),
)
