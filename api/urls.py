from django.urls import path
from api import views

urlpatterns = [
    path("notify/", views.notify)
]
