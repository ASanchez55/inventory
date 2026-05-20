from django import forms

from .models import Inventory, StockMovement


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['reorder_level']

    def clean_reorder_level(self):
        reorder_level = self.cleaned_data['reorder_level']
        if reorder_level < 0:
            raise forms.ValidationError("Reorder level cannot be negative.")
        return reorder_level


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['quantity', 'reference']

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
