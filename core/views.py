from django.db.models import F, Sum
from django.shortcuts import render
from orders.models import Order
from products.models import Product


def dashboard(request):
    orders = Order.objects.prefetch_related("items")
    return render(request, "core/dashboard.html", {
        "product_count": Product.objects.count(),
        "stock_total": Product.objects.aggregate(total=Sum("stock_quantity"))["total"] or 0,
        "low_stock": Product.objects.filter(stock_quantity__lte=F("minimum_stock")).count(),
        "pending_orders": Order.objects.filter(status=Order.Status.PENDING).count(),
        "orders_total": sum((order.total for order in orders), 0),
    })
