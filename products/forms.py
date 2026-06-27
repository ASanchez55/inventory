from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import (
    Brand,
    Category,
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
)


def apply_bootstrap_classes(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs['class'] = 'form-check-input'
            continue

        css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
        existing_classes = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = f'{existing_classes} {css_class}'.strip()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_classes(self)

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        qs = Category.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "A category with this name already exists.")
        return name


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_classes(self)

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        qs = Brand.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "A brand with this name already exists.")
        return name


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'lead_time_days', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_classes(self)
        self.fields['notes'].widget.attrs['rows'] = 4

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        qs = Supplier.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "A supplier with this name already exists.")
        return name


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'brand', 'supplier', 'price']

    def clean_sku(self):
        sku = self.cleaned_data['sku'].strip()
        qs = Product.objects.filter(sku__iexact=sku)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "A product with this SKU already exists.")
        return sku

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('name')
        self.fields['brand'].queryset = Brand.objects.order_by('name')
        self.fields['supplier'].queryset = Supplier.objects.order_by('name')
        self.fields['supplier'].required = False
        apply_bootstrap_classes(self)


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'status', 'order_date', 'expected_date', 'notes']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.order_by('name')
        self.fields['status'].choices = [
            (PurchaseOrder.STATUS_DRAFT, 'Draft'),
            (PurchaseOrder.STATUS_ORDERED, 'Ordered'),
            (PurchaseOrder.STATUS_CANCELLED, 'Cancelled'),
        ]
        apply_bootstrap_classes(self)

    def clean(self):
        cleaned_data = super().clean()
        order_date = cleaned_data.get('order_date')
        expected_date = cleaned_data.get('expected_date')

        if order_date and expected_date and expected_date < order_date:
            self.add_error(
                'expected_date',
                'Expected date cannot be earlier than the order date.',
            )

        return cleaned_data


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity_ordered', 'unit_cost']
        widgets = {
            'quantity_ordered': forms.NumberInput(attrs={'min': 1}),
            'unit_cost': forms.NumberInput(attrs={'min': 0.01, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.select_related(
            'category',
            'brand',
        ).order_by('name')
        apply_bootstrap_classes(self)


class BasePurchaseOrderItemFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if 'DELETE' in form.fields:
            form.fields['DELETE'].widget.attrs['class'] = 'form-check-input'

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        has_item = False
        product_ids = set()

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            if form.cleaned_data.get('DELETE'):
                continue

            product = form.cleaned_data.get('product')
            quantity = form.cleaned_data.get('quantity_ordered')
            unit_cost = form.cleaned_data.get('unit_cost')

            if not product and not quantity and not unit_cost:
                continue

            if not product or not quantity or unit_cost is None:
                raise forms.ValidationError('Complete each purchase order item row.')

            if quantity <= 0:
                raise forms.ValidationError('Quantity ordered must be greater than zero.')

            if unit_cost <= 0:
                raise forms.ValidationError('Unit cost must be greater than zero.')

            if product.pk in product_ids:
                raise forms.ValidationError(
                    'Each product should appear only once in a purchase order.',
                )

            product_ids.add(product.pk)
            has_item = True

        if not has_item:
            raise forms.ValidationError('Add at least one purchase order item.')


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    formset=BasePurchaseOrderItemFormSet,
    extra=5,
    can_delete=True,
)
