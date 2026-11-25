from django import forms
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from products.models import Product


class OrderItemForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    quantity = forms.IntegerField(min_value=1)


class BaseOrderItemFormSet(forms.BaseFormSet):
    def add_non_form_error(self, message):
        self._non_form_errors = self.error_class([message])

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        product_ids = [
            form.cleaned_data["product"].pk
            for form in self.forms
            if form.cleaned_data and form.cleaned_data.get("product")
        ]
        if len(product_ids) != len(set(product_ids)):
            raise ValidationError("Um produto não pode aparecer mais de uma vez no pedido.")


OrderItemFormSet = formset_factory(
    OrderItemForm,
    formset=BaseOrderItemFormSet,
    extra=1,
    min_num=1,
    validate_min=True,
)
