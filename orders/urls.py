from django.urls import path
from . import views

urlpatterns = [
    path("", views.order_list, name="order-list"),
    path("novo/", views.order_create, name="order-create"),
    path("<int:pk>/", views.order_detail, name="order-detail"),
    path("<int:pk>/cancelar/", views.order_cancel, name="order-cancel"),
]
