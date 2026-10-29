from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField("nome", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("nome", max_length=150)
    description = models.TextField("descrição", blank=True)
    sku = models.CharField("SKU", max_length=40, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField("preço", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    stock_quantity = models.PositiveIntegerField("estoque", default=0)
    minimum_stock = models.PositiveIntegerField("estoque mínimo", default=0)
    created_at = models.DateTimeField("cadastrado em", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gt=0), name="product_price_positive"),
            models.CheckConstraint(condition=models.Q(stock_quantity__gte=0), name="product_stock_nonnegative"),
            models.CheckConstraint(condition=models.Q(minimum_stock__gte=0), name="product_minimum_nonnegative"),
        ]

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.minimum_stock

    def __str__(self):
        return f"{self.name} ({self.sku})"
