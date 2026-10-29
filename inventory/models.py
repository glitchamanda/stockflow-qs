from django.core.validators import MinValueValidator
from django.db import models
from products.models import Product


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN = "IN", "Entrada"
        OUT = "OUT", "Saída"

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=3, choices=MovementType.choices)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reason = models.CharField("motivo", max_length=255)
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.PROTECT, related_name="movements")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gt=0), name="movement_quantity_positive")]
