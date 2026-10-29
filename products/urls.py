from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product-list"),
    path("novo/", views.product_create, name="product-create"),
    path("<int:pk>/", views.product_detail, name="product-detail"),
    path("<int:pk>/editar/", views.product_update, name="product-update"),
    path("<int:pk>/excluir/", views.product_delete, name="product-delete"),
    path("categorias/", views.category_list, name="category-list"),
    path("categorias/nova/", views.category_create, name="category-create"),
]
