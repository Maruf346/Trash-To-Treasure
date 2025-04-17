from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
import uuid 
from django.db import models
from django.utils.text import slugify

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

    # New fields
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    listing_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.material_name} - {self.trash_point}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.material_name}-{self.trash_point}")
        super().save(*args, **kwargs)


# Upcycled Products Model
class UpcycledProduct(models.Model):
    product_name = models.CharField(max_length=255, default="")
    category = models.CharField(max_length=100, default="")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_status = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES, default='active')
    
    # Replacing name/contact with a ForeignKey to Artisan user
    artisan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upcycled_products', null=True, blank=True)

    approval_status = models.BooleanField(default=False)
    stock_availability = models.IntegerField()
    product_images = models.ImageField(upload_to='upcycled_products/', blank=True, null=True)
    location = models.CharField(max_length=255, default="")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    tags = models.CharField(max_length=255, blank=True, null=True)
    listing_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    sold_count = models.IntegerField(default=0)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='ready')
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return f"{self.product_name} by {self.artisan.username if self.artisan else 'Unknown'}"

    def save(self, *args, **kwargs):
        if not self.slug:
            artisan_username = self.artisan.username if self.artisan else 'unknown-artisan'
            self.slug = slugify(f"{self.product_name}-{artisan_username}")
        super().save(*args, **kwargs)
