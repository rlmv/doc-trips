


from django.conf.urls import patterns, url, include

from db.urlhelpers import DB_REGEX
from croos.views import (EditCrooApplication, NewCrooApplication,
                         CreateCrooApplication, RedirectToNextGradableCrooApplication, 
                         GradeCrooApplication, NoCrooApplicationsLeftToGrade,
                         CrooApplicationDatabaseListView, CrooApplicationDatabaseDetailView,
                         CrooApplicationDatabaseUpdateView, CrooListView, 
                         CrooCreateView, CrooUpdateView, CrooDetailView, 
                         CrooDeleteView)

urlpatterns = patterns('', 
    url(r'^apply/$', NewCrooApplication.as_view(), name='apply'),
    url(r'^apply/edit$', EditCrooApplication.as_view(), name='edit_application'),
    url(r'^createapplication/$', CreateCrooApplication.as_view(), name='create_application'),                   
    url(r'^grade/$', RedirectToNextGradableCrooApplication.as_view(), name='grade_next'),
    url(r'^grade/(?P<pk>[0-9]+)$', GradeCrooApplication.as_view(), name='grade'),
    url(r'^grade/none/$', NoCrooApplicationsLeftToGrade.as_view(), name='no_applications'),
)

crooapplication_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], CrooApplicationDatabaseListView.as_view(), name='crooapplication_index'),
    url(DB_REGEX['DETAIL'], CrooApplicationDatabaseDetailView.as_view(), name='crooapplication_detail'),
    url(DB_REGEX['UPDATE'], CrooApplicationDatabaseUpdateView.as_view(), name='crooapplication_update'),
)

croo_urlpatterns = patterns(
    '',
    url(DB_REGEX['LIST'], CrooListView.as_view(), name='croo_index'),
    url(DB_REGEX['CREATE'], CrooCreateView.as_view(), name='croo_create'),
    url(DB_REGEX['UPDATE'], CrooUpdateView.as_view(), name='croo_update'),
    url(DB_REGEX['DETAIL'], CrooDetailView.as_view(), name='croo_detail'),
    url(DB_REGEX['DELETE'], CrooDeleteView.as_view(), name='croo_delete')
)
                        
