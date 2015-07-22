
from django.conf.urls import url

from doc.db.urlhelpers import DB_REGEX
from doc.transport.views import *

scheduledtransport_urlpatterns = [
    url(DB_REGEX['LIST'], ScheduledTransportMatrix.as_view(),
        name='scheduledtransport_index'),
    url(DB_REGEX['CREATE'], ScheduledTransportCreateView.as_view(),
        name='scheduledtransport_create'),
    url(DB_REGEX['DELETE'], ScheduledTransportDeleteView.as_view(),
        name='scheduledtransport_delete'),
    url(r'^ordering/(?P<bus_pk>[0-9]+)/$', OrderStops.as_view(),
        name='scheduledtransport_order'),
]

externalbus_urlpatterns = [
    url(DB_REGEX['LIST'], ExternalBusMatrix.as_view(),
        name='externalbus_matrix'),
    url(DB_REGEX['CREATE'], ExternalBusCreate.as_view(),
        name='externalbus_create'),
    url(DB_REGEX['DELETE'], ExternalBusDelete.as_view(),
        name='externalbus_delete'),
]

transportstop_urlpatterns = [
    url(DB_REGEX['LIST'], StopListView.as_view(), name='stop_index'),
    url(DB_REGEX['CREATE'], StopCreateView.as_view(), name='stop_create'),
    url(DB_REGEX['DETAIL'], StopDetailView.as_view(), name='stop_detail'),
    url(DB_REGEX['UPDATE'], StopUpdateView.as_view(), name='stop_update'),
    url(DB_REGEX['DELETE'], StopDeleteView.as_view(), name='stop_delete'),
]

route_urlpatterns = [
     url(DB_REGEX['LIST'], RouteListView.as_view(), name='route_index'),
    url(DB_REGEX['CREATE'], RouteCreateView.as_view(), name='route_create'),
    url(DB_REGEX['DETAIL'], RouteDetailView.as_view(), name='route_detail'),
    url(DB_REGEX['UPDATE'], RouteUpdateView.as_view(), name='route_update'),
    url(DB_REGEX['DELETE'], RouteDeleteView.as_view(), name='route_delete'),
]

vehicle_urlpatterns = [
    url(DB_REGEX['LIST'], VehicleListView.as_view(), name='vehicle_index'),
    url(DB_REGEX['CREATE'], VehicleCreateView.as_view(), name='vehicle_create'),
    url(DB_REGEX['DETAIL'], VehicleDetailView.as_view(), name='vehicle_detail'),
    url(DB_REGEX['UPDATE'], VehicleUpdateView.as_view(), name='vehicle_update'),
    url(DB_REGEX['DELETE'], VehicleDeleteView.as_view(), name='vehicle_delete'),
]
