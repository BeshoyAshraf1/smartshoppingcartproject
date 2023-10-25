from rest_framework import routers, serializers, viewsets
from .models import Customer,Cart,Order,OrderItem,OrderItemProduct,Product


#retrieve and convert all customer data to json

class Customerserializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


