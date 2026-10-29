from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from products.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        CONFIRMED = "CONFIRMED", "Confirmado"
        CANCELLED = "CANCELLED", "Cancelado"
        COMPLETED = "COMPLETED", "Concluído"

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return sum((item.subtotal for item in self.items.all()), Decimal("0.00"))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gt=0), name="order_item_quantity_positive")]
