from django.urls import re_path

from .consumers import CompanyDashboardConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/companies/(?P<slug>[-\w]+)/dashboard/$",
        CompanyDashboardConsumer.as_asgi(),
    ),
]
