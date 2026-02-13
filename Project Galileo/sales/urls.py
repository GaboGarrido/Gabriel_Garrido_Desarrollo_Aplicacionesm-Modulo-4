from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CustomerViewSet, ProductViewSet, SaleViewSet, DashboardView, InventoryTransactionViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'inventory', InventoryTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
