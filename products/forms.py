from django import forms
from .models import Category, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "sku", "category", "price", "minimum_stock"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
