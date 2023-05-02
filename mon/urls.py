from django.urls import path
from .views import MON, CHECK

urlpatterns = [
    path("", MON.as_view()),
    path("check/", CHECK.as_view()),
]
