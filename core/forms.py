from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import AdminNote, BulkPrice, Order, Product, Review, User, InventoryAlert


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}))
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your address'}),
        required=True,
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'address', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter your password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number'].strip()
        if not phone.isdigit():
            raise forms.ValidationError('Use numbers only for the phone number.')
        return phone


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'sku', 'description', 'image', 'price', 'quantity', 'reorder_level']


class ProductSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search by name or SKU...'})
    )
    category = forms.CharField(
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Filter by category...'})
    )
    low_stock = forms.BooleanField(required=False, label='Low stock only')


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'quantity']

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get('product')
        quantity = cleaned.get('quantity') or 0
        if product and quantity > product.quantity:
            raise forms.ValidationError('Requested quantity is higher than available stock.')
        return cleaned


class OrderFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + list(Order.STATUS_CHOICES)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class AdminNoteForm(forms.ModelForm):
    class Meta:
        model = AdminNote
        fields = ['title', 'body']
        widgets = {'body': forms.Textarea(attrs={'rows': 4})}


class PhoneResetRequestForm(forms.Form):
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
    )

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number'].strip()
        if not phone.isdigit():
            raise forms.ValidationError('Use numbers only for the phone number.')
        return phone


class PasswordResetConfirmForm(forms.Form):
    code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Enter the 6-digit code'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('new_password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i}★') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience (optional)'}),
        }


class BulkPriceForm(forms.ModelForm):
    class Meta:
        model = BulkPrice
        fields = ['quantity_min', 'discount_percent']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'role']


class TwoFactorForm(forms.Form):
    enable_2fa = forms.BooleanField(required=False, label='Enable Two-Factor Authentication')
