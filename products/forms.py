from django import forms

from .models import Category, Brand


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

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

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        qs = Brand.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "A brand with this name already exists.")
        return name
