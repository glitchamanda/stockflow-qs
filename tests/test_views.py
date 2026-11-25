import pytest
from django.core.management import call_command
from django.urls import reverse
from products.models import Category, Product


@pytest.mark.django_db
def test_dashboard_uses_database(client):
    category = Category.objects.create(name="Casa")
    Product.objects.create(name="Caneca", sku="C-1", category=category, price="12.50", stock_quantity=4, minimum_stock=5)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200
    assert response.context["product_count"] == 1
    assert response.context["low_stock"] == 1


@pytest.mark.django_db
def test_product_search(client):
    category = Category.objects.create(name="Casa")
    Product.objects.create(name="Caneca", sku="C-1", category=category, price="12.50")
    response = client.get(reverse("product-list"), {"q": "C-1"})
    assert response.status_code == 200
    assert b"Caneca" in response.content


@pytest.mark.django_db
def test_product_create_and_movement_pages(client):
    category = Category.objects.create(name="Casa")
    response = client.post(reverse("product-create"), {
        "name": "Prato", "sku": "P-1", "category": category.pk,
        "price": "10.00", "minimum_stock": 1,
    })
    assert response.status_code == 302
    product = Product.objects.get(sku="P-1")
    response = client.post(reverse("movement-create"), {
        "product": product.pk, "movement_type": "IN", "quantity": 5, "reason": "Compra",
    })
    assert response.status_code == 302
    product.refresh_from_db()
    assert product.stock_quantity == 5


@pytest.mark.django_db
def test_order_pages_create_and_cancel(client):
    category = Category.objects.create(name="Casa")
    product = Product.objects.create(name="Copo", sku="C-2", category=category, price="4.00", stock_quantity=3)
    response = client.post(reverse("order-create"), {"product": product.pk, "quantity": 2})
    assert response.status_code == 302
    order_id = response.url.rstrip("/").split("/")[-1]
    response = client.post(reverse("order-cancel", kwargs={"pk": order_id}))
    assert response.status_code == 302
    product.refresh_from_db()
    assert product.stock_quantity == 3


@pytest.mark.django_db
def test_seed_demo_is_idempotent_and_creates_expected_data():
    call_command("seed_demo")
    call_command("seed_demo")
    assert Category.objects.count() == 3
    assert Product.objects.count() == 6


@pytest.mark.django_db
def test_category_create(client):
    response = client.post(reverse("category-create"), {"name": "Escritório"})

    assert response.status_code == 302
    assert response.url == reverse("category-list")
    assert Category.objects.filter(name="Escritório").exists()


@pytest.mark.django_db
def test_product_detail_update_and_delete(client):
    category = Category.objects.create(name="Casa")
    product = Product.objects.create(
        name="Caneca", sku="C-1", category=category, price="12.50", stock_quantity=4
    )

    detail_response = client.get(reverse("product-detail", kwargs={"pk": product.pk}))
    assert detail_response.status_code == 200
    assert b"Caneca" in detail_response.content

    update_response = client.post(reverse("product-update", kwargs={"pk": product.pk}), {
        "name": "Caneca Azul", "sku": "C-1", "category": category.pk,
        "description": "Caneca para café", "price": "15.00", "minimum_stock": 2,
    })
    assert update_response.status_code == 302
    product.refresh_from_db()
    assert product.name == "Caneca Azul"

    delete_response = client.post(reverse("product-delete", kwargs={"pk": product.pk}))
    assert delete_response.status_code == 302
    assert not Product.objects.filter(pk=product.pk).exists()


@pytest.mark.django_db
def test_product_category_filter(client):
    casa = Category.objects.create(name="Casa")
    eletronicos = Category.objects.create(name="Eletrônicos")
    Product.objects.create(name="Copo", sku="C-1", category=casa, price="5.00")
    Product.objects.create(name="Mouse", sku="M-1", category=eletronicos, price="50.00")

    response = client.get(reverse("product-list"), {"category": casa.pk})

    assert response.status_code == 200
    assert b"Copo" in response.content
    assert b"Mouse" not in response.content


@pytest.mark.django_db
def test_product_low_stock_filter(client):
    category = Category.objects.create(name="Casa")
    Product.objects.create(
        name="Prato", sku="P-1", category=category, price="10.00",
        stock_quantity=2, minimum_stock=3,
    )
    Product.objects.create(
        name="Talher", sku="T-1", category=category, price="4.00",
        stock_quantity=10, minimum_stock=3,
    )

    response = client.get(reverse("product-list"), {"stock": "low"})

    assert response.status_code == 200
    assert b"Prato" in response.content
    assert b"Talher" not in response.content


@pytest.mark.django_db
def test_order_create_rejects_insufficient_stock(client):
    category = Category.objects.create(name="Casa")
    product = Product.objects.create(
        name="Copo", sku="C-1", category=category, price="4.00", stock_quantity=1
    )

    response = client.post(reverse("order-create"), {"product": product.pk, "quantity": 2})

    assert response.status_code == 200
    assert b"Estoque insuficiente" in response.content
    product.refresh_from_db()
    assert product.stock_quantity == 1
