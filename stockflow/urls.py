from django.contrib import admin
from django.urls import include, path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("produtos/", include("products.urls")),
    path("estoque/", include("inventory.urls")),
    path("pedidos/", include("orders.urls")),
]
