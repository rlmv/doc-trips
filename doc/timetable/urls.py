

from django.conf.urls import patterns, url

from timetable.views import TimetableEditView


urlpatterns = patterns('', 
    url(r'^$', TimetableEditView.as_view(), name='timetable'),    
)
        
