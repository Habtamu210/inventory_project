from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import (
    User,
    Request,
    Product,
    Item,
    BusinessUnit,
    ProductCategory,
    UnitOfMeasurement,
)

# -----------------------------
# User Registration / Edit Forms
# -----------------------------
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
# -----------------------------
# Request Form
# -----------------------------
class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['product', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RequestForm, self).__init__(*args, **kwargs)
        # Optionally filter products available for requesting
        if user:
            self.fields['product'].queryset = Product.objects.filter(is_active=True)


# -----------------------------
# Product Form
# -----------------------------
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'unit_of_measurement', 'price_per_unit', 'reorder_level', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product name'}),
        }


# -----------------------------
# Item Form
# -----------------------------
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'product',
            'serial_number',
            'purchase_date',
            'condition',
            'status',
            'location',
            'warranty_expiry_date',
            'assigned_to',
            'business_unit',
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


# -----------------------------
# Business Unit Form
# -----------------------------
class BusinessUnitForm(forms.ModelForm):
    class Meta:
        model = BusinessUnit
        fields = ['name', 'director']


# -----------------------------
# Product Category Form
# -----------------------------
class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name']


# -----------------------------
# Unit Of Measurement Form
# -----------------------------
class UnitOfMeasurementForm(forms.ModelForm):
    class Meta:
        model = UnitOfMeasurement
        fields = ['name', 'abbreviation']
