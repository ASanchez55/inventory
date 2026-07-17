from django import forms

from .models import Inventory, StockMovement


def apply_bootstrap_classes(form):
    for field in form.fields.values():
        css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
        existing_classes = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = f'{existing_classes} {css_class}'.strip()


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['reorder_level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_classes(self)

    def clean_reorder_level(self):
        reorder_level = self.cleaned_data['reorder_level']
        if reorder_level < 0:
            raise forms.ValidationError("Reorder level cannot be negative.")
        return reorder_level


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['quantity', 'reference']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_classes(self)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
