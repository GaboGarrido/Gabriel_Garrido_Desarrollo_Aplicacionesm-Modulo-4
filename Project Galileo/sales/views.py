from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from .models import Customer, Product, Sale
from .serializers import CustomerSerializer, ProductSerializer, SaleSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from .serializers import InventoryTransactionSerializer
from .models import InventoryTransaction
from django.db import transaction
from decimal import Decimal


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    queryset = InventoryTransaction.objects.select_related('product').all().order_by('-created_at')
    serializer_class = InventoryTransactionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DashboardView(APIView):
    """Return aggregated metrics for the frontend dashboard."""
    def get(self, request, format=None):
        # use unit_price when present, otherwise fall back to product.price
        total_expr = ExpressionWrapper(
            F('quantity') * Coalesce(F('unit_price'), F('product__price')), output_field=FloatField()
        )
        total_sales_amount = Sale.objects.aggregate(
            total=Sum(total_expr)
        )['total'] or 0

        total_sales_count = Sale.objects.count()
        total_products_sold = Sale.objects.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

        revenue_expr = ExpressionWrapper(F('sale__quantity') * Coalesce(F('sale__unit_price'), F('price')), output_field=FloatField())
        top_products_qs = Product.objects.annotate(
            total_qty=Sum('sale__quantity'),
            revenue=Sum(revenue_expr)
        ).order_by('-total_qty')[:5]

        top_products = [
            {
                'id': p.id,
                'name': p.name,
                'total_qty': p.total_qty or 0,
                'revenue': round(p.revenue or 0, 2)
            }
            for p in top_products_qs
        ]

        return Response({
            'total_sales_amount': round(total_sales_amount or 0, 2),
            'total_sales_count': total_sales_count,
            'total_products_sold': total_products_sold,
            'top_products': top_products,
        })


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('name')
    serializer_class = CustomerSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('product', 'customer').all().order_by('-created_at')
    serializer_class = SaleSerializer

    def create(self, request, *args, **kwargs):
        # accept nested payload or simple ids
        data = request.data
        # handle customer
        cust_data = data.get('customer')
        if isinstance(cust_data, dict):
            cust, _ = Customer.objects.get_or_create(name=cust_data.get('name'), defaults={'email': cust_data.get('email', '')})
        else:
            cust = get_object_or_404(Customer, pk=cust_data)

        prod_data = data.get('product')
        if isinstance(prod_data, dict):
            prod, _ = Product.objects.get_or_create(name=prod_data.get('name'), defaults={'price': prod_data.get('price', 0)})
        else:
            prod = get_object_or_404(Product, pk=prod_data)

        qty = int(data.get('quantity', 1))
        # unit price can be provided (sale price) or fall back to product price
        unit_price_val = data.get('unit_price')
        if unit_price_val is not None:
            unit_price = Decimal(str(unit_price_val))
        else:
            unit_price = prod.price

        # create sale and corresponding inventory transaction atomically
        try:
            with transaction.atomic():
                sale = Sale.objects.create(customer=cust, product=prod, quantity=qty, unit_price=unit_price)
                # record stock out
                inv = InventoryTransaction(product=prod, quantity=qty, type=InventoryTransaction.TYPE_OUT, note=f'Sale #{sale.id}')
                inv.save()
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SaleSerializer(sale)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
