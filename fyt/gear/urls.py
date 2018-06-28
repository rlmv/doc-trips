from django.urls import path

from fyt.gear.views import *


gear_urlpatterns = [
    path('', GearList.as_view(), name='list'),
    path('create/', GearCreate.as_view(), name='create'),
    path('<int:pk>/update/', GearUpdate.as_view(), name='update'),
]
