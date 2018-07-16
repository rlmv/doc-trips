from django.urls import path

from fyt.gear.views import *


gear_urlpatterns = [
    path('', GearList.as_view(), name='list'),
    path('create/', GearCreate.as_view(), name='create'),
    path('<int:pk>/update/', GearUpdate.as_view(), name='update'),
]

gear_request_urlpatterns = [
    path('', GearRequestList.as_view(), name='list'),
]

urlpatterns = [
    path('request/', RequestGear.as_view(), name='request'),
]
