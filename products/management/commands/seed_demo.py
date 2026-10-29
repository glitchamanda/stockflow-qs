from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import StockMovement
from inventory.services import move_stock
from orders.models import Order
from orders.services import cancel_order, create_order
from products.models import Category, Product


class Command(BaseCommand):
    help = "Insere categorias, produtos, movimentações e pedidos para demonstração."

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for name in ("Eletrônicos", "Escritório", "Casa"):
            categories[name], _ = Category.objects.get_or_create(name=name)

        product_data = [
            ("Mouse sem fio", "ELEC-MOUSE-001", "Eletrônicos", "79.90", 18, 5),
            ("Teclado mecânico", "ELEC-KEY-001", "Eletrônicos", "249.90", 7, 3),
            ("Monitor 24 polegadas", "ELEC-MON-001", "Eletrônicos", "899.00", 2, 4),
            ("Caderno universitário", "ESCR-CAD-001", "Escritório", "24.90", 30, 10),
            ("Caneta azul", "ESCR-CAN-001", "Escritório", "3.50", 60, 20),
            ("Garrafa térmica", "CASA-GAR-001", "Casa", "89.90", 12, 4),
        ]
        products = {}
        for name, sku, category, price, quantity, minimum in product_data:
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "category": categories[category],
                    "price": price,
                    "minimum_stock": minimum,
                },
            )
            products[sku] = product
            if created and quantity:
                move_stock(product.pk, StockMovement.MovementType.IN, quantity, "Carga de demonstração")

        mouse = products["ELEC-MOUSE-001"]
        keyboard = products["ELEC-KEY-001"]
        if not Order.objects.filter(movements__reason="Pedido de demonstração pendente").exists():
            pending = create_order([(mouse.pk, 2), (keyboard.pk, 1)])
            pending.movements.update(reason="Pedido de demonstração pendente")

        bottle = products["CASA-GAR-001"]
        if not Order.objects.filter(movements__reason="Pedido de demonstração cancelado").exists():
            cancelled = create_order([(bottle.pk, 1)])
            cancelled.movements.update(reason="Pedido de demonstração cancelado")
            cancel_order(cancelled.pk)
            cancelled.movements.filter(movement_type=StockMovement.MovementType.IN).update(
                reason="Pedido de demonstração cancelado"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Dados prontos: {Category.objects.count()} categorias, "
            f"{Product.objects.count()} produtos e {Order.objects.count()} pedidos."
        ))
