from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review
from django.contrib.contenttypes.models import ContentType

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_product_rating(sender, instance, **kwargs):
    content_object = instance.content_object
    if hasattr(content_object, 'update_average_rating'):
        content_object.update_average_rating()
