import pytest
from django.core.management import call_command
from django.urls import reverse
from inventory.models import StockMovement
from inventory.services import move_stock
from orders.models import Order
from products.forms import ProductForm
from products.models import Category, Product


@pytest.mark.django_db
def test_dashboard_uses_database(client):
    category = Category.objects.create(name="Casa")
    Product.objects.create(name="Caneca", sku="C-1", category=category, price="12.50", stock_quantity=4, minimum_stock=5)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200
    assert response.context["product_count"] == 1
    assert response.context["stock_value_total"] == 50
    assert response.context["low_stock"] == 1
    assert b"R$ 50,00" in response.content


@pytest.mark.django_db
def test_dashboard_empty_database_has_zero_indicators(client):
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200
    assert response.context["product_count"] == 0
    assert response.context["stock_total"] == 0
    assert response.context["stock_value_total"] == 0
    assert response.context["low_stock"] == 0
    assert response.context["pending_orders"] == 0
    assert response.context["orders_total"] == 0


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
        "price": "10.00", "cost": "6.25", "minimum_stock": 1,

    })
    assert response.status_code == 302
    product = Product.objects.get(sku="P-1")
    assert str(product.cost) == "6.25"
    response = client.get(reverse("product-detail", kwargs={"pk": product.pk}))
    assert b"6,25" in response.content
    response = client.post(reverse("movement-create"), {
        "product": product.pk, "movement_type": "IN", "quantity": 5, "reason": "Compra",
    })
    assert response.status_code == 302
    product.refresh_from_db()
    assert product.stock_quantity == 5


@pytest.mark.django_db
def test_product_update_rejects_cost_above_sale_price(client):
    category = Category.objects.create(name="Casa")
    product = Product.objects.create(
        name="Caneca", sku="C-3", category=category, price="20.00", cost="10.00",
    )

    response = client.post(reverse("product-update", kwargs={"pk": product.pk}), {
        "name": product.name,
        "description": product.description,
        "sku": product.sku,
        "category": category.pk,
        "price": "20.00",
        "cost": "25.00",
        "minimum_stock": product.minimum_stock,
    })

    assert response.status_code == 200
    assert response.context["form"].has_error("cost")
    product.refresh_from_db()
    assert product.cost == 10


@pytest.mark.django_db
def test_order_pages_create_and_cancel(client):
    category = Category.objects.create(name="Casa")
    product = Product.objects.create(name="Copo", sku="C-2", category=category, price="4.00", stock_quantity=3)
    response = client.post(reverse("order-create"), {
        "items-TOTAL_FORMS": 1,
        "items-INITIAL_FORMS": 0,
        "items-MIN_NUM_FORMS": 1,
        "items-MAX_NUM_FORMS": 1000,
        "items-0-product": product.pk,
        "items-0-quantity": 2,
    })
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
def test_category_name_must_be_unique(client):
    Category.objects.create(name="Casa")
    response = client.post(reverse("category-create"), {"name": "Casa"})
    assert response.status_code == 200
    assert Category.objects.filter(name="Casa").count() == 1


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

    response = client.post(reverse("order-create"), {
        "items-TOTAL_FORMS": 1,
        "items-INITIAL_FORMS": 0,
        "items-MIN_NUM_FORMS": 1,
        "items-MAX_NUM_FORMS": 1000,
        "items-0-product": product.pk,
        "items-0-quantity": 2,
    })

    assert response.status_code == 200
    assert b"Estoque insuficiente" in response.content
    product.refresh_from_db()
    assert product.stock_quantity == 1


@pytest.mark.django_db
def test_product_form_rejects_duplicate_sku_and_invalid_costs(client):
    category = Category.objects.create(name="Casa")
    Product.objects.create(name="Existente", sku="SKU-1", category=category, price="10.00")

    duplicate = ProductForm(data={
        "name": "Outro", "sku": "SKU-1", "category": category.pk,
        "price": "10.00", "cost": "5.00", "minimum_stock": 0,
    })
    assert not duplicate.is_valid()
    assert "sku" in duplicate.errors

    negative_cost = ProductForm(data={
        "name": "Produto", "sku": "SKU-2", "category": category.pk,
        "price": "10.00", "cost": "-1.00", "minimum_stock": 0,
    })
    assert not negative_cost.is_valid()
    assert "cost" in negative_cost.errors

    cost_above_price = ProductForm(data={
        "name": "Produto", "sku": "SKU-3", "category": category.pk,
        "price": "10.00", "cost": "12.00", "minimum_stock": 0,
    })
    assert not cost_above_price.is_valid()


@pytest.mark.django_db
def test_product_and_category_with_history_cannot_be_deleted(client):
    category = Category.objects.create(name="Casa")
    product = Product.objects.create(name="Caneca", sku="C-10", category=category, price="12.50")
    move_stock(product.pk, StockMovement.MovementType.IN, 1, "Entrada")

    product_response = client.post(reverse("product-delete", kwargs={"pk": product.pk}))
    category_response = client.post(reverse("category-delete", kwargs={"pk": category.pk}))

    assert product_response.status_code == 302
    assert category_response.status_code == 302
    assert Product.objects.filter(pk=product.pk).exists()
    assert Category.objects.filter(pk=category.pk).exists()
    assert StockMovement.objects.filter(product=product).exists()


@pytest.mark.django_db
def test_category_without_products_can_be_deleted(client):
    category = Category.objects.create(name="Temporária")
    response = client.post(reverse("category-delete", kwargs={"pk": category.pk}))
    assert response.status_code == 302
    assert not Category.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
def test_order_form_accepts_multiple_products(client):
    category = Category.objects.create(name="Casa")
    cup = Product.objects.create(
        name="Copo", sku="C-20", category=category, price="4.00", stock_quantity=5,
    )
    plate = Product.objects.create(
        name="Prato", sku="P-20", category=category, price="8.00", stock_quantity=4,
    )
    response = client.post(reverse("order-create"), {
        "items-TOTAL_FORMS": 2,
        "items-INITIAL_FORMS": 0,
        "items-MIN_NUM_FORMS": 1,
        "items-MAX_NUM_FORMS": 1000,
        "items-0-product": cup.pk,
        "items-0-quantity": 2,
        "items-1-product": plate.pk,
        "items-1-quantity": 1,
    })

    assert response.status_code == 302
    order = Order.objects.get()
    assert order.items.count() == 2
    assert order.total == 16
    cup.refresh_from_db()
    plate.refresh_from_db()
    assert cup.stock_quantity == 3
    assert plate.stock_quantity == 3


@pytest.mark.django_db
def test_order_form_requires_at_least_one_item(client):
    response = client.post(reverse("order-create"), {
        "items-TOTAL_FORMS": 0,
        "items-INITIAL_FORMS": 0,
        "items-MIN_NUM_FORMS": 1,
        "items-MAX_NUM_FORMS": 1000,
    })
    assert response.status_code == 200
    assert not Order.objects.exists()


@pytest.mark.django_db
def test_order_form_rejects_duplicate_products_without_changing_stock(client):
    category = Category.objects.create(name="Casa")
    product = Product.objects.create(
        name="Copo", sku="C-21", category=category, price="4.00", stock_quantity=5,
    )
    response = client.post(reverse("order-create"), {
        "items-TOTAL_FORMS": 2,
        "items-INITIAL_FORMS": 0,
        "items-MIN_NUM_FORMS": 1,
        "items-MAX_NUM_FORMS": 1000,
        "items-0-product": product.pk,
        "items-0-quantity": 1,
        "items-1-product": product.pk,
        "items-1-quantity": 2,
    })

    assert response.status_code == 200
    assert "mais de uma vez" in response.context["formset"].non_form_errors()[0]
    assert not Order.objects.exists()
    product.refresh_from_db()
    assert product.stock_quantity == 5


@pytest.mark.django_db
def test_order_status_actions_follow_allowed_transitions(client):
    from orders.services import create_order

    category = Category.objects.create(name="Casa")
    product = Product.objects.create(
        name="Copo", sku="C-22", category=category, price="4.00", stock_quantity=3,
    )
    order = create_order([(product.pk, 1)])

    confirmed = client.post(reverse("order-confirm", kwargs={"pk": order.pk}))
    assert confirmed.status_code == 302
    order.refresh_from_db()
    assert order.status == Order.Status.CONFIRMED

    completed = client.post(reverse("order-complete", kwargs={"pk": order.pk}))
    assert completed.status_code == 302
    order.refresh_from_db()
    assert order.status == Order.Status.COMPLETED

    client.post(reverse("order-cancel", kwargs={"pk": order.pk}))
    order.refresh_from_db()
    product.refresh_from_db()
    assert order.status == Order.Status.COMPLETED
    assert product.stock_quantity == 2
