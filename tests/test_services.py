import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from inventory.models import StockMovement
from inventory.services import move_stock
from orders.models import Order
from orders.services import cancel_order, complete_order, confirm_order, create_order
from products.models import Category, Product


@pytest.fixture
def product(db):
    category = Category.objects.create(name="Eletrônicos")
    return Product.objects.create(name="Mouse", sku="M-1", category=category, price="50.00", stock_quantity=10, minimum_stock=2)


def test_stock_entry_and_exit_update_balance(product):
    move_stock(product.pk, "IN", 5, "Compra")
    move_stock(product.pk, "OUT", 3, "Venda")
    product.refresh_from_db()
    assert product.stock_quantity == 12
    assert StockMovement.objects.count() == 2


def test_stock_exit_cannot_overdraw(product):
    with pytest.raises(ValidationError):
        move_stock(product.pk, "OUT", 11, "Venda")
    product.refresh_from_db()
    assert product.stock_quantity == 10
    assert not StockMovement.objects.exists()


def test_order_records_price_and_decreases_stock(product):
    order = create_order([(product.pk, 2)])
    product.price = "80.00"
    product.save(update_fields=["price"])
    item = order.items.get()
    assert item.unit_price == 50
    assert order.total == 100
    product.refresh_from_db()
    assert product.stock_quantity == 8


def test_order_is_atomic_when_one_item_has_insufficient_stock(product):
    other = Product.objects.create(name="Teclado", sku="T-1", category=product.category, price="100.00", stock_quantity=1)
    with pytest.raises(ValidationError):
        create_order([(product.pk, 2), (other.pk, 2)])
    assert not Order.objects.exists()
    product.refresh_from_db()
    assert product.stock_quantity == 10


def test_cancel_returns_stock_only_once(product):
    order = create_order([(product.pk, 3)])
    cancel_order(order.pk)
    cancel_order(order.pk)
    product.refresh_from_db()
    assert product.stock_quantity == 10
    assert StockMovement.objects.filter(movement_type="IN").count() == 1


def test_duplicate_sku_is_rejected(product):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Product.objects.create(
                name="Outro mouse",
                sku=product.sku,
                category=product.category,
                price="20.00",
            )


def test_negative_price_is_rejected(product):
    product.price = "-1.00"
    with pytest.raises(ValidationError):
        product.full_clean()


def test_negative_stock_and_movement_quantity_are_rejected(product):
    product.stock_quantity = -1
    with pytest.raises(ValidationError):
        product.full_clean()
    with pytest.raises(ValidationError):
        move_stock(product.pk, "IN", 0, "Carga inválida")


def test_invalid_movement_type_is_rejected_without_changes(product):
    with pytest.raises(ValidationError):
        move_stock(product.pk, "TRANSFER", 2, "Tipo desconhecido")
    product.refresh_from_db()
    assert product.stock_quantity == 10
    assert not StockMovement.objects.exists()


def test_order_with_non_positive_quantity_is_rejected(product):
    with pytest.raises(ValidationError):
        create_order([(product.pk, 0)])


def test_duplicate_product_in_order_is_rejected_atomically(product):
    with pytest.raises(ValidationError, match="mais de uma vez"):
        create_order([(product.pk, 2), (product.pk, 1)])
    product.refresh_from_db()
    assert product.stock_quantity == 10
    assert not Order.objects.exists()
    assert not StockMovement.objects.exists()


def test_order_status_transitions_and_invalid_transitions(product):
    order = create_order([(product.pk, 1)])
    with pytest.raises(ValidationError):
        complete_order(order.pk)

    confirm_order(order.pk)
    with pytest.raises(ValidationError):
        confirm_order(order.pk)
    complete_order(order.pk)
    with pytest.raises(ValidationError):
        cancel_order(order.pk)

    order.refresh_from_db()
    assert order.status == Order.Status.COMPLETED
    product.refresh_from_db()
    assert product.stock_quantity == 9


def test_confirmed_order_can_be_cancelled_and_returns_stock(product):
    order = create_order([(product.pk, 2)])
    confirm_order(order.pk)
    cancel_order(order.pk)
    order.refresh_from_db()
    product.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
    assert product.stock_quantity == 10