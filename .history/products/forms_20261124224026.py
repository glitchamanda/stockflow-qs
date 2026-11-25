from django import forms
from .models import Category, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "sku", "category", "price", "cost", "minimum_stock"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get("price")
        cost = cleaned_data.get("cost")
        if price is not None and cost is not None and cost > price:
            self.add_error("cost", "O custo não pode ser maior que o preço de venda.")
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
