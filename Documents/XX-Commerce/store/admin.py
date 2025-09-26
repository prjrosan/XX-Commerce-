from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json
import csv
from .models import (
    Category, Product, ProductImage, Address, Cart, CartItem, 
    Order, OrderItem, Coupon, Wishlist
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'parent', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    ordering = ['name']
    
    def has_add_permission(self, request):
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'price', 'compare_price', 'price_yen', 'compare_price_yen', 
        'stock_quantity', 'get_sales_count', 'is_active', 'is_featured', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_featured', 'category', 'track_inventory', 
        'allow_backorder', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description', 'meta_title']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'compare_price', 'stock_quantity', 'is_active', 'is_featured']
    inlines = [ProductImageInline]
    ordering = ['-created_at']
    actions = [
        'make_active', 'make_inactive', 'make_featured', 'make_unfeatured', 
        'restock_products', 'bulk_price_update', 'export_products', 'duplicate_products'
    ]
    
    def price_yen(self, obj):
        return f"¥{obj.price:,.0f}"
    price_yen.short_description = 'Price (JPY)'
    price_yen.admin_order_field = 'price'
    
    def compare_price_yen(self, obj):
        if obj.compare_price:
            return f"¥{obj.compare_price:,.0f}"
        return "-"
    compare_price_yen.short_description = 'Compare Price (JPY)'
    compare_price_yen.admin_order_field = 'compare_price'
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} products were successfully marked as active.')
    make_active.short_description = "Mark selected products as active"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} products were successfully marked as inactive.')
    make_inactive.short_description = "Mark selected products as inactive"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} products were successfully marked as featured.')
    make_featured.short_description = "Mark selected products as featured"
    
    def make_unfeatured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} products were successfully marked as unfeatured.')
    make_unfeatured.short_description = "Mark selected products as unfeatured"
    
    def get_sales_count(self, obj):
        """Display total sales count for this product."""
        from django.db.models import Sum
        total_sold = OrderItem.objects.filter(product=obj).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        return f"{total_sold:,}"
    get_sales_count.short_description = 'Total Sold'
    get_sales_count.admin_order_field = 'orderitem__quantity'
    
    def restock_products(self, request, queryset):
        """Restock selected products to a default quantity."""
        restock_quantity = 100  # Default restock quantity
        updated = queryset.update(stock_quantity=restock_quantity)
        self.message_user(request, f'{updated} products were restocked to {restock_quantity} units.')
    restock_products.short_description = "Restock selected products to 100 units"
    
    def bulk_price_update(self, request, queryset):
        """Bulk update prices for selected products."""
        if request.POST.get('post'):
            price_increase = float(request.POST.get('price_increase', 0))
            price_multiplier = float(request.POST.get('price_multiplier', 1.0))
            
            updated = 0
            for product in queryset:
                if price_increase > 0:
                    product.price += price_increase
                if price_multiplier != 1.0:
                    product.price *= price_multiplier
                product.save()
                updated += 1
            
            self.message_user(request, f'{updated} products were updated.')
            return
        
        context = {
            'queryset': queryset,
            'action_name': 'bulk_price_update',
        }
        return render(request, 'admin/bulk_price_update.html', context)
    bulk_price_update.short_description = "Bulk update prices"
    
    def export_products(self, request, queryset):
        """Export selected products to CSV."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Name', 'SKU', 'Category', 'Price', 'Compare Price', 'Stock', 
            'Active', 'Featured', 'Created At'
        ])
        
        for product in queryset:
            writer.writerow([
                product.name,
                product.sku,
                product.category.name,
                product.price,
                product.compare_price or '',
                product.stock_quantity,
                product.is_active,
                product.is_featured,
                product.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_products.short_description = "Export selected products to CSV"
    
    def duplicate_products(self, request, queryset):
        """Duplicate selected products."""
        duplicated = 0
        for product in queryset:
            # Create a copy
            product.pk = None
            product.name = f"{product.name} (Copy)"
            product.sku = f"{product.sku}_COPY_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            product.slug = f"{product.slug}-copy-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            product.save()
            
            # Copy images
            for image in product.images.all():
                image.pk = None
                image.product = product
                image.save()
            
            duplicated += 1
        
        self.message_user(request, f'{duplicated} products were duplicated.')
    duplicate_products.short_description = "Duplicate selected products"
    
    def has_add_permission(self, request):
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'track_inventory', 'allow_backorder')
        }),
        ('Product Details', {
            'fields': ('weight', 'dimensions')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    list_editable = ['is_primary', 'sort_order']
    ordering = ['product', 'sort_order']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = "Preview"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'address_type', 'first_name', 'last_name', 
        'city', 'state', 'is_default', 'created_at'
    ]
    list_filter = ['address_type', 'is_default', 'country', 'created_at']
    search_fields = ['user__username', 'first_name', 'last_name', 'city', 'state']
    ordering = ['-created_at']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['line_total']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'total_items', 'total_price_yen', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['total_items', 'total_price']
    ordering = ['-created_at']
    
    def total_price_yen(self, obj):
        return f"¥{obj.total_price:,.0f}"
    total_price_yen.short_description = 'Total (JPY)'
    total_price_yen.admin_order_field = 'total_price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'line_total_yen', 'created_at']
    list_filter = ['created_at']
    search_fields = ['cart__user__username', 'product__name']
    ordering = ['-created_at']
    
    def line_total_yen(self, obj):
        return f"¥{obj.line_total:,.0f}"
    line_total_yen.short_description = 'Line Total (JPY)'
    line_total_yen.admin_order_field = 'line_total'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['line_total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'payment_status', 
        'total_amount_yen', 'total_items', 'get_items_sold', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__username', 'tracking_number']
    readonly_fields = ['order_number', 'total_items', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    actions = [
        'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled',
        'export_orders', 'send_tracking_emails', 'bulk_status_update'
    ]
    
    def total_amount_yen(self, obj):
        return f"¥{obj.total_amount:,.0f}"
    total_amount_yen.short_description = 'Total (JPY)'
    total_amount_yen.admin_order_field = 'total_amount'
    
    def get_items_sold(self, obj):
        """Display total items sold in this order."""
        from django.db.models import Sum
        total_items = obj.items.aggregate(total=Sum('quantity'))['total'] or 0
        return f"{total_items:,}"
    get_items_sold.short_description = 'Items Sold'
    get_items_sold.admin_order_field = 'items__quantity'
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders were marked as processing.')
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders were marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders were marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} orders were marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected orders as cancelled"
    
    def export_orders(self, request, queryset):
        """Export selected orders to CSV."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Customer', 'Status', 'Payment Status', 'Total Amount',
            'Items Count', 'Created At', 'Tracking Number'
        ])
        
        for order in queryset:
            writer.writerow([
                order.order_number,
                order.user.username if order.user else 'Guest',
                order.status,
                order.payment_status,
                order.total_amount,
                order.total_items,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.tracking_number or ''
            ])
        
        return response
    export_orders.short_description = "Export selected orders to CSV"
    
    def send_tracking_emails(self, request, queryset):
        """Send tracking emails for shipped orders."""
        sent = 0
        for order in queryset.filter(status='shipped', tracking_number__isnull=False):
            # Here you would implement email sending logic
            # For now, just count the orders that would receive emails
            sent += 1
        
        self.message_user(request, f'Tracking emails would be sent for {sent} orders.')
    send_tracking_emails.short_description = "Send tracking emails for shipped orders"
    
    def bulk_status_update(self, request, queryset):
        """Bulk update order status."""
        if request.POST.get('post'):
            new_status = request.POST.get('new_status')
            updated = queryset.update(status=new_status)
            self.message_user(request, f'{updated} orders were updated to {new_status}.')
            return
        
        context = {
            'queryset': queryset,
            'action_name': 'bulk_status_update',
            'status_choices': Order.ORDER_STATUS,
        }
        return render(request, 'admin/bulk_status_update.html', context)
    bulk_status_update.short_description = "Bulk update order status"
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Additional Information', {
            'fields': ('notes', 'tracking_number', 'shipped_at', 'delivered_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'shipping_address', 'billing_address')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'product_sku', 'quantity', 'price_yen', 'line_total_yen', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product_name', 'product_sku']
    readonly_fields = ['line_total']
    ordering = ['-created_at']
    
    def price_yen(self, obj):
        return f"¥{obj.price:,.0f}"
    price_yen.short_description = 'Price (JPY)'
    price_yen.admin_order_field = 'price'
    
    def line_total_yen(self, obj):
        return f"¥{obj.line_total:,.0f}"
    line_total_yen.short_description = 'Line Total (JPY)'
    line_total_yen.admin_order_field = 'line_total'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'description', 'coupon_type', 'value', 
        'used_count', 'usage_limit', 'is_active', 'valid_until'
    ]
    list_filter = ['coupon_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'description', 'coupon_type', 'value')
        }),
        ('Usage Limits', {
            'fields': ('minimum_amount', 'maximum_discount', 'usage_limit', 'used_count')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']
    ordering = ['-created_at']


# Customize admin site
admin.site.site_header = "XX Commerce Administration"
admin.site.site_title = "XX Commerce Admin"
admin.site.index_title = "Welcome to XX Commerce Administration"

# Custom admin URLs are handled in the main urls.py file

# Custom admin views are handled in admin_views.py and main urls.py