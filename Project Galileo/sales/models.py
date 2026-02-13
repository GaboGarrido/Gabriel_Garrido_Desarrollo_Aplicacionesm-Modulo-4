from django.db import models
from django.db.models import F


class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.name} (${self.price})"


class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        price = self.unit_price if self.unit_price is not None else self.product.price
        return self.quantity * price

    def __str__(self):
        return f"Sale #{self.id} - {self.product.name} x{self.quantity}"


class InventoryTransaction(models.Model):
    TYPE_IN = 'IN'
    TYPE_OUT = 'OUT'
    TYPE_CHOICES = [(TYPE_IN, 'Entrada'), (TYPE_OUT, 'Salida')]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.PositiveIntegerField()
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Adjust product stock on first save
        is_new = self.pk is None
        if is_new:
            if self.type == self.TYPE_IN:
                self.product.stock = F('stock') + self.quantity
                self.product.save()
            else:
                # OUT
                # ensure enough stock
                # refresh from db
                self.product.refresh_from_db()
                if self.product.stock - self.quantity < 0:
                    raise ValueError('Insufficient stock')
                self.product.stock = F('stock') - self.quantity
                self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_display()} {self.quantity} x {self.product.name} ({self.created_at.date()})"
