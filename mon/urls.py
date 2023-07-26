from django.urls import path
from .views import MON

urlpatterns = [
    path("", MON.as_view())
]
