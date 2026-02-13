from rest_framework import serializers
from .models import Customer, Product, Sale


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'reorder_point']


class InventoryTransactionSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = None
        # will be set dynamically below


# set Meta.model to InventoryTransaction to avoid circular import issues
from .models import InventoryTransaction
InventoryTransactionSerializer.Meta.model = InventoryTransaction
InventoryTransactionSerializer.Meta.fields = ['id', 'product', 'quantity', 'type', 'note', 'created_at']


class SaleSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    product = ProductSerializer()

    class Meta:
        model = Sale
        fields = ['id', 'customer', 'product', 'quantity', 'unit_price', 'created_at', 'total']
