from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Permission
from django.db.models import Q

User = get_user_model()

MODULE_PERMISSION_FILTER = (
    Q(content_type__app_label='products', codename='access_products_module')
    | Q(content_type__app_label='products', codename='access_suppliers_module')
    | Q(content_type__app_label='inventory_app', codename='access_inventory_module')
    | Q(content_type__app_label='users', codename='access_users_module')
    | Q(content_type__app_label='users', codename='access_reports_module')
)


def add_widget_class(field, css_class):
    existing_classes = field.widget.attrs.get('class', '')
    field.widget.attrs['class'] = f'{existing_classes} {css_class}'.strip()


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            add_widget_class(field, 'form-control')


class PendingApprovalAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            add_widget_class(field, 'form-control')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        try:
            return super().clean()
        except forms.ValidationError:
            user = User._default_manager.filter(username=username).first()
            if user and not user.is_active and user.check_password(password):
                raise forms.ValidationError(
                    'Your account is pending administrator approval.',
                    code='inactive',
                )
            raise


class UserAccessForm(forms.ModelForm):
    module_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Choose which modules this user can access.',
    )

    class Meta:
        model = User
        fields = ('is_active', 'module_permissions')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_widget_class(self.fields['is_active'], 'form-check-input')
        self.fields['module_permissions'].queryset = Permission.objects.filter(
            MODULE_PERMISSION_FILTER
        ).order_by('content_type__app_label')
        self.fields['module_permissions'].label_from_instance = self._permission_label
        if self.instance.pk:
            self.fields['module_permissions'].initial = self.instance.user_permissions.filter(
                MODULE_PERMISSION_FILTER
            )

    @staticmethod
    def _permission_label(permission):
        labels = {
            ('products', 'access_products_module'): 'Products',
            ('products', 'access_suppliers_module'): 'Suppliers',
            ('inventory_app', 'access_inventory_module'): 'Inventory',
            ('users', 'access_users_module'): 'Users',
            ('users', 'access_reports_module'): 'Reports',
        }
        return labels.get(
            (permission.content_type.app_label, permission.codename),
            permission.name,
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        module_permissions = list(self.cleaned_data['module_permissions'])
        existing_permissions = Permission.objects.filter(MODULE_PERMISSION_FILTER)

        if commit:
            user.user_permissions.remove(*existing_permissions)
            user.user_permissions.add(*module_permissions)
        else:
            self._pending_module_permissions = module_permissions

        return user

    def save_m2m(self):
        super().save_m2m()
        if hasattr(self, '_pending_module_permissions'):
            existing_permissions = Permission.objects.filter(MODULE_PERMISSION_FILTER)
            self.instance.user_permissions.remove(*existing_permissions)
            self.instance.user_permissions.add(*self._pending_module_permissions)
