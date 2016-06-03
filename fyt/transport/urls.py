
from django.conf.urls import url

from fyt.db.urlhelpers import DB_REGEX
from fyt.transport.views import *

scheduledtransport_urlpatterns = [
    url(DB_REGEX['LIST'], ScheduledTransportMatrix.as_view(),
        name='index'),
    url(DB_REGEX['CREATE'], ScheduledTransportCreateView.as_view(),
        name='create'),
    url(DB_REGEX['UPDATE'], ScheduledTransportUpdateView.as_view(),
        name='update'),
    url(DB_REGEX['DELETE'], ScheduledTransportDeleteView.as_view(),
        name='delete'),
    url(r'^ordering/(?P<bus_pk>[0-9]+)/$', OrderStops.as_view(),
        name='order'),
    url(r'^(?P<route_pk>[0-9]+)/(?P<date>[0-9]+-[0-9]+-[0-9]+)/$',
        TransportChecklist.as_view(), name='checklist'),
    url(r'^packet/$', InternalBusPacket.as_view(), name='packet'),
    url(r'^packet/for/(?P<date>[0-9]+-[0-9]+-[0-9]+)/$',
        InternalBusPacketForDate.as_view(), name='packet_for_date'),
]

externalbus_urlpatterns = [
    url(DB_REGEX['LIST'], ExternalBusMatrix.as_view(), name='matrix'),
    url(DB_REGEX['CREATE'], ExternalBusCreate.as_view(), name='create'),
    url(DB_REGEX['DELETE'], ExternalBusDelete.as_view(), name='delete'),
    url(r'^packet/$', ExternalBusPacket.as_view(), name='packet'),
    url(r'^packet/for/(?P<date>[0-9]+-[0-9]+-[0-9]+)/$',
        ExternalBusPacketForDate.as_view(), name='packet_for_date'),
    url(r'^packet/for/(?P<date>[0-9]+-[0-9]+-[0-9]+)/(?P<route_pk>[0-9]+)$',
        ExternalBusPacketForDateAndRoute.as_view(),
        name='packet_for_date_and_route'),
    url(r'^(?P<route_pk>[0-9]+)/(?P<section_pk>[0-9]+)/$',
        ExternalBusChecklist.as_view(), name='checklist'),
]

stop_urlpatterns = [
    url(DB_REGEX['LIST'], StopListView.as_view(), name='index'),
    url(DB_REGEX['CREATE'], StopCreateView.as_view(), name='create'),
    url(DB_REGEX['DETAIL'], StopDetailView.as_view(), name='detail'),
    url(DB_REGEX['UPDATE'], StopUpdateView.as_view(), name='update'),
    url(DB_REGEX['DELETE'], StopDeleteView.as_view(), name='delete'),
]

route_urlpatterns = [
    url(DB_REGEX['LIST'], RouteListView.as_view(), name='index'),
    url(DB_REGEX['CREATE'], RouteCreateView.as_view(), name='create'),
    url(DB_REGEX['DETAIL'], RouteDetailView.as_view(), name='detail'),
    url(DB_REGEX['UPDATE'], RouteUpdateView.as_view(), name='update'),
    url(DB_REGEX['DELETE'], RouteDeleteView.as_view(), name='delete'),
]

vehicle_urlpatterns = [
    url(DB_REGEX['LIST'], VehicleListView.as_view(), name='index'),
    url(DB_REGEX['CREATE'], VehicleCreateView.as_view(), name='create'),
    url(DB_REGEX['DETAIL'], VehicleDetailView.as_view(), name='detail'),
    url(DB_REGEX['UPDATE'], VehicleUpdateView.as_view(), name='update'),
    url(DB_REGEX['DELETE'], VehicleDeleteView.as_view(), name='delete'),
]
