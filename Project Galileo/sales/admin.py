from django.contrib import admin
from .models import Customer, Product, Sale

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Sale)

from .models import InventoryTransaction
admin.site.register(InventoryTransaction)
