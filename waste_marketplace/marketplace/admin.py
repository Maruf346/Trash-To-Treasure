from django.contrib import admin
from .models import TrashItem
from .models import TrashItem, UpcycledProduct, Order, OrderItem, CartItem 


admin.site.register(TrashItem)
admin.site.register(UpcycledProduct)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)
# Register your models here.
