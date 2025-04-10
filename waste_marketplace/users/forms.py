# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

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
