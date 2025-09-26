"""
URL configuration for xxcommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from store import admin_views

urlpatterns = [
    # Custom admin URLs must come before the main admin URL
    path("admin/sales-dashboard/", admin_views.sales_dashboard, name="admin_sales_dashboard"),
    path("admin/inventory/", admin_views.inventory_management, name="admin_inventory"),
    path("admin/customers/", admin_views.customer_analytics, name="admin_customer_analytics"),
    path("admin/products/analytics/", admin_views.product_analytics, name="admin_product_analytics"),
    path("admin/orders/analytics/", admin_views.order_analytics, name="admin_order_analytics"),
    path("admin/bulk-operations/", admin_views.bulk_operations, name="admin_bulk_operations"),
    path("admin/export/", admin_views.export_data, name="admin_export_data"),
    # Main admin URL comes after custom URLs
    path("admin/", admin.site.urls),
    path("", include("store.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("store.auth_urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
