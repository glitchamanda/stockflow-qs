from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import OrderItemFormSet
from .models import Order
from .services import cancel_order, complete_order, confirm_order, create_order


def order_list(request):
    return render(request, "orders/order_list.html", {"orders": Order.objects.all()})


def order_detail(request, pk):
    return render(request, "orders/order_detail.html", {"order": get_object_or_404(Order, pk=pk)})


def order_create(request):
    formset = OrderItemFormSet(request.POST or None, prefix="items")
    if request.method == "POST" and formset.is_valid():
        items = [
            (form.cleaned_data["product"].pk, form.cleaned_data["quantity"])
            for form in formset
            if form.cleaned_data
        ]
        try:
            order = create_order(items)
        except ValidationError as error:
            formset.add_non_form_error(error.message)
        else:
            messages.success(request, "Pedido criado e estoque atualizado.")
            return redirect("order-detail", pk=order.pk)
    return render(request, "orders/order_form.html", {"formset": formset, "title": "Novo pedido"})


@require_POST
def order_confirm(request, pk):
    order = get_object_or_404(Order, pk=pk)
    try:
        confirm_order(order.pk)
    except ValidationError as error:
        messages.error(request, error.message)
    else:
        messages.success(request, "Pedido confirmado.")
    return redirect("order-detail", pk=pk)


@require_POST
def order_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    try:
        complete_order(order.pk)
    except ValidationError as error:
        messages.error(request, error.message)
    else:
        messages.success(request, "Pedido concluído.")
    return redirect("order-detail", pk=pk)


@require_POST
def order_cancel(request, pk):
    try:
        cancel_order(pk)
    except ValidationError as error:
        messages.error(request, error.message)
    else:
        messages.success(request, "Pedido cancelado e estoque devolvido.")
    return redirect("order-detail", pk=pk)
