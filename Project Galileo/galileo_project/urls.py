from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('sales.urls')),
    path('', TemplateView.as_view(template_name='sales/index.html'), name='home'),
]
