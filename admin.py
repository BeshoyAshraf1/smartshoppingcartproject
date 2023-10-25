from django.contrib import admin
from .models import Customer,Product,Cart,Order,OrderItem,OrderItemProduct,CartMembership
# Register your models here.

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(OrderItem)
admin.site.register(OrderItemProduct)
admin.site.register(CartMembership)