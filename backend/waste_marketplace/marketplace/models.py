from django.db import models
from django.contrib.auth import get_user_model
import uuid 
from django.db import models


User = get_user_model()

# Choices for condition, status, and delivery state
CONDITION_CHOICES = [
    ('new', 'New'),
    ('used', 'Used'),
    ('damaged', 'Damaged'),
]

PRODUCT_STATUS_CHOICES = [
    ('active', 'Active'),
    ('sold_out', 'Sold Out'),
    ('inactive', 'Inactive'),
]

DELIVERY_STATUS_CHOICES = [
    ('ready', 'Ready'),
    ('packed', 'Packed'),
    ('on_the_way', 'On its way'),
    ('delivered', 'Delivered'),
]

# Waste Materials Model
class TrashItem(models.Model):
    #product_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    material_name = models.CharField(max_length=255, default="")  # Change as needed
    category = models.CharField(max_length=100, default="")  # Change as needed
    description = models.TextField()
    condition = models.CharField(max_length=50, default="")  # Set a meaningful default
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    trash_point = models.CharField(max_length=255, default="")  # Set a meaningful default
    images = models.ImageField(upload_to='waste_images/', blank=True, null=True)
    location = models.CharField(max_length=255, default="")  # Set a meaningful default
    product_status = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES, default='')
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='')

    def __str__(self):
        return f"{self.material_name} - {self.trash_point}"


# Upcycled Products Model
class UpcycledProduct(models.Model):
    #product_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    product_name = models.CharField(max_length=255, default="")
    category = models.CharField(max_length=100, default="")  # Change as needed
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_status = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES, default='')
    artisan_name = models.CharField(max_length=255)
    artisan_contact_info = models.CharField(max_length=255)
    approval_status = models.BooleanField(default=False)  # Admin Approval
    stock_availability = models.IntegerField()
    product_images = models.ImageField(upload_to='upcycled_products/', blank=True, null=True)
    location = models.CharField(max_length=255, default="")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # e.g., 4.5 rating
    tags = models.CharField(max_length=255, blank=True, null=True)  # Optional field

    def __str__(self):
        return f"{self.product_name} by {self.artisan_name}"


# Create your models here.
