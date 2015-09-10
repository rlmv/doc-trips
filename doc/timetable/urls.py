from django.conf.urls import url

from .views import EditTimetable


urlpatterns = [
    url(r'^$', EditTimetable.as_view(), name='timetable'),
]
      
