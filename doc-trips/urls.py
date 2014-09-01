from django.conf.urls import patterns, include, url

# default Django admin interface
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'views.index', name='home'),                      
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^db/', include('db.urls', namespace='db')),
    url(r'^leader/', include('leader.urls', namespace='leader')),
    url(r'^admin/', include(admin.site.urls)),
)

from user.models import GlobalPermission
from django.contrib.auth.models import Group

can_grade, ct = GlobalPermission.objects.get_or_create(codename='can_grade_applications', 
                                                   name='Can grade leader applications')
can_access_db, ct = GlobalPermission.objects.get_or_create(codename='can_access_db',
                                                       name='Can access trips database')
                                                       
directors, ct = Group.objects.get_or_create(name='directors')
directors.permissions = [can_grade, can_access_db]
directors.save()

graders, ct = Group.objects.get_or_create(name='graders')
graders.permissions = [can_grade]
graders.save()

