
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

# Choices for role and account status
ROLE_CHOICES = (
    ('driver', 'Driver'),
    ('artisan', 'Artisan'),
    ('buyer', 'Buyer'),
)

ACCOUNT_STATUS_CHOICES = (
    ('active', 'Active'),
    ('suspended', 'Suspended'),
    ('deleted', 'Deleted'),
)

class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUS_CHOICES, default='active')

    objects = CustomUserManager()  # ✅ Use your custom manager
    
    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'

    def __str__(self):
        return f"{self.username} ({self.role})"


# Driver-specific data
class DriverProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    delivery_area = models.CharField(max_length=100, blank=True)
    delivery_count = models.PositiveIntegerField(default=0)
    order_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"DriverProfile - {self.user.username}"


# Artisan-specific data
class ArtisanProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    product_category = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    product_approval_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    order_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"ArtisanProfile - {self.user.username}"


# Buyer-specific data
class BuyerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    loyalty_points = models.PositiveIntegerField(default=0)
    order_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"BuyerProfile - {self.user.username}"
