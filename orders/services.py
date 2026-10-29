from django.core.exceptions import ValidationError
from django.db import transaction
from inventory.models import StockMovement
from products.models import Product
from .models import Order, OrderItem


@transaction.atomic
def create_order(items):
    if not items:
        raise ValidationError("O pedido deve conter pelo menos um item.")
    order = Order.objects.create()
    for product_id, quantity in items:
        if quantity <= 0:
            raise ValidationError("A quantidade de cada item deve ser maior que zero.")
        product = Product.objects.select_for_update().get(pk=product_id)
        if product.stock_quantity < quantity:
            raise ValidationError(f"Estoque insuficiente para {product.name}.")
        product.stock_quantity -= quantity
        product.save(update_fields=["stock_quantity"])
        OrderItem.objects.create(order=order, product=product, quantity=quantity, unit_price=product.price)
        StockMovement.objects.create(
            product=product, movement_type=StockMovement.MovementType.OUT,
            quantity=quantity, reason=f"Pedido #{order.pk}", order=order,
        )
    return order


@transaction.atomic
def cancel_order(order_id):
    order = Order.objects.select_for_update().get(pk=order_id)
    if order.status == Order.Status.CANCELLED:
        return order
    if order.status == Order.Status.COMPLETED:
        raise ValidationError("Pedidos concluídos não podem ser cancelados.")
    for item in order.items.select_related("product"):
        product = Product.objects.select_for_update().get(pk=item.product_id)
        product.stock_quantity += item.quantity
        product.save(update_fields=["stock_quantity"])
        StockMovement.objects.create(
            product=product, movement_type=StockMovement.MovementType.IN,
            quantity=item.quantity, reason=f"Cancelamento do pedido #{order.pk}", order=order,
        )
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])
    return order
