from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
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


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'price_yen', 'stock_quantity', 
        'is_active', 'is_featured', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_featured', 'category', 'track_inventory', 
        'allow_backorder', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description', 'meta_title']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['stock_quantity', 'is_active', 'is_featured']
    inlines = [ProductImageInline]
    ordering = ['-created_at']
    
    def price_yen(self, obj):
        return f"¥{obj.price:,.0f}"
    price_yen.short_description = 'Price (JPY)'
    price_yen.admin_order_field = 'price'
    
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
        'total_amount_yen', 'total_items', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__username', 'tracking_number']
    readonly_fields = ['order_number', 'total_items', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    
    def total_amount_yen(self, obj):
        return f"¥{obj.total_amount:,.0f}"
    total_amount_yen.short_description = 'Total (JPY)'
    total_amount_yen.admin_order_field = 'total_amount'
    
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