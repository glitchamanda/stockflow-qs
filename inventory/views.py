from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import StockMovementForm
from .models import StockMovement
from .services import move_stock


def movement_list(request):
    movements = StockMovement.objects.select_related("product", "order")
    return render(request, "inventory/movement_list.html", {"movements": movements})


def movement_create(request):
    form = StockMovementForm(request.POST or None)
    if form.is_valid():
        try:
            data = form.cleaned_data
            move_stock(data["product"].pk, data["movement_type"], data["quantity"], data["reason"])
        except Exception as error:
            form.add_error(None, str(error))
        else:
            messages.success(request, "Movimentação registrada.")
            return redirect("movement-list")
    return render(request, "form.html", {"form": form, "title": "Nova movimentação"})
