from django import forms
from django.contrib.auth.models import User
from .models import Address, Coupon


class AddToCartForm(forms.Form):
    """Form for adding products to cart."""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '100',
            'value': '1'
        })
    )


class AddressForm(forms.ModelForm):
    """Form for creating/editing addresses."""
    class Meta:
        model = Address
        fields = [
            'address_type', 'first_name', 'last_name', 'company',
            'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'phone', 'is_default'
        ]
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CheckoutForm(forms.Form):
    """Form for checkout process."""
    shipping_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        empty_label="Select shipping address",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    billing_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        empty_label="Select billing address",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    use_billing_as_shipping = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Special instructions for your order...'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['shipping_address'].queryset = Address.objects.filter(
                user=user, address_type='shipping'
            )
            self.fields['billing_address'].queryset = Address.objects.filter(
                user=user, address_type='billing'
            )


class CouponForm(forms.Form):
    """Form for applying coupons."""
    code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code'
        })
    )


class UserRegistrationForm(forms.ModelForm):
    """Form for user registration."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
