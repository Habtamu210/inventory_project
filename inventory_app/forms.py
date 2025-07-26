from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import (
    User, Request, Product, Item, BusinessUnit,
    ProductCategory, UnitOfMeasurement, Transaction
)
from inventory_app import models

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'business_unit', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'business_unit', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class AdminUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm',  # minimized height
            'placeholder': 'Enter password'
        }),
        help_text=None
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Confirm password'
        }),
        help_text=None
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'business_unit', 'role', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].lower()
        user.email = email
        user.username = email  # Ensure username is email
        if commit:
            user.save()
        return user

# --- Product and Related Forms ---
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'unit_of_measurement', 'price_per_unit', 'reorder_level', 'is_active']


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'product', 'serial_number', 'purchase_date', 'condition', 'status',
            'location', 'warranty_expiry_date', 'assigned_to', 'business_unit'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class BusinessUnitForm(forms.ModelForm):
    class Meta:
        model = BusinessUnit
        fields = ['name', 'director']


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name']


class UnitOfMeasurementForm(forms.ModelForm):
    class Meta:
        model = UnitOfMeasurement
        fields = ['name', 'abbreviation']


# --- Request Form ---
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
        if user:
            self.fields['product'].queryset = Product.objects.filter(is_active=True)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


# --- Transaction Form ---
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'item',
            'expected_return_date',
            'condition_on_borrow',
            'remarks',
        ]
        widgets = {
            'expected_return_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = Item.objects.filter(status='Available')
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
