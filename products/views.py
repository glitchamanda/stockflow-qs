from django.contrib import messages
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CategoryForm, ProductForm
from .models import Category, Product


def product_list(request):
    products = Product.objects.select_related("category").all()
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    stock = request.GET.get("stock", "")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if category:
        products = products.filter(category_id=category)
    if stock == "low":
        products = products.filter(stock_quantity__lte=F("minimum_stock"))
    return render(request, "products/product_list.html", {"products": products, "categories": Category.objects.all()})


def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Produto cadastrado.")
        return redirect("product-list")
    return render(request, "form.html", {"form": form, "title": "Novo produto"})


def product_detail(request, pk):
    return render(request, "products/product_detail.html", {"product": get_object_or_404(Product, pk=pk)})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Produto atualizado.")
        return redirect("product-detail", pk=pk)
    return render(request, "form.html", {"form": form, "title": "Editar produto"})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Produto excluído.")
        return redirect("product-list")
    return render(request, "confirm_delete.html", {"object": product})


def category_list(request):
    return render(request, "products/category_list.html", {"categories": Category.objects.all()})


def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("category-list")
    return render(request, "form.html", {"form": form, "title": "Nova categoria"})
