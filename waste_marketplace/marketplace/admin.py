from django.contrib import admin
from .models import TrashItem
from .models import TrashItem, UpcycledProduct


admin.site.register(TrashItem)
admin.site.register(UpcycledProduct)
# Register your models here.
