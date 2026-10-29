from django.urls import path
from . import views

urlpatterns = [
    path("", views.movement_list, name="movement-list"),
    path("nova/", views.movement_create, name="movement-create"),
]
