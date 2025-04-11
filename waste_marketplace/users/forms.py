# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import BuyerProfile


class CustomUserSignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('driver', 'Delivery Guy'),
        ('artisan', 'Artisan'),
    ]

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'role', 'password1', 'password2']


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'email', 'phone', 'account_status']
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),  # Make username read-only
        }

class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = ['loyalty_points', 'order_number']
        widgets = {
            'loyalty_points': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'order_number': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }