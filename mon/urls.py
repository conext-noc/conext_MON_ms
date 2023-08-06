from django.urls import path
from .views import MON, Summary, Alarms, Deactivate, PortVerify, AllClients

urlpatterns = [
    path("", MON.as_view()),
    path("summary", Summary.as_view()),
    path("alarms", Alarms.as_view()),
    path("deactivates", Deactivate.as_view()),
    path("port", PortVerify.as_view()),
    path("total", AllClients.as_view()),
]
