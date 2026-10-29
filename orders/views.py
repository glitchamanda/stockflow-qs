from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from .forms import OrderForm
from .models import Order
from .services import cancel_order, create_order


def order_list(request):
    return render(request, "orders/order_list.html", {"orders": Order.objects.all()})


def order_detail(request, pk):
    return render(request, "orders/order_detail.html", {"order": get_object_or_404(Order, pk=pk)})


def order_create(request):
    form = OrderForm(request.POST or None)
    if form.is_valid():
        try:
            order = create_order([(form.cleaned_data["product"].pk, form.cleaned_data["quantity"])])
        except ValidationError as error:
            form.add_error(None, error.message)
        else:
            messages.success(request, "Pedido criado e estoque atualizado.")
            return redirect("order-detail", pk=order.pk)
    return render(request, "form.html", {"form": form, "title": "Novo pedido"})


def order_cancel(request, pk):
    if request.method == "POST":
        try:
            cancel_order(pk)
        except ValidationError as error:
            messages.error(request, error.message)
        else:
            messages.success(request, "Pedido cancelado e estoque devolvido.")
    return redirect("order-detail", pk=pk)
