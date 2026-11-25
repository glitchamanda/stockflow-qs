from django.core.exceptions import ValidationError
from django.db import transaction
from products.models import Product
from .models import StockMovement


@transaction.atomic
def move_stock(product_id, movement_type, quantity, reason, order=None):
    if movement_type not in StockMovement.MovementType.values:
        raise ValidationError("Tipo de movimentação inválido.")
    if quantity <= 0:
        raise ValidationError("A quantidade deve ser maior que zero.")
    product = Product.objects.select_for_update().get(pk=product_id)
    delta = quantity if movement_type == StockMovement.MovementType.IN else -quantity
    product.stock_quantity += delta
    product.save(update_fields=["stock_quantity"])
    return StockMovement.objects.create(
        product=product, movement_type=movement_type, quantity=quantity, reason=reason, order=order
    )
