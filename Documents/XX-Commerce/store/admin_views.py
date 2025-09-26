from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from .models import Product, Order, OrderItem, Category, User, Cart, Wishlist
from django.contrib.auth.decorators import user_passes_test
import json
import csv

@staff_member_required
def sales_dashboard(request):
    """Sales dashboard for admin users."""
    
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Sales statistics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Recent sales (last 7 days)
    recent_orders = Order.objects.filter(created_at__date__gte=week_ago)
    recent_revenue = recent_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:10]
    
    # Sales by category (simplified - just count items sold)
    category_sales = Category.objects.annotate(
        total_sales=Sum('products__orderitem__quantity')
    ).filter(total_sales__gt=0).order_by('-total_sales')
    
    # Order status distribution
    order_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Low stock products
    low_stock_products = Product.objects.filter(
        stock_quantity__lt=10,
        track_inventory=True,
        is_active=True
    ).order_by('stock_quantity')
    
    # Recent orders
    recent_orders_list = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_revenue': recent_revenue,
        'top_products': top_products,
        'category_sales': category_sales,
        'order_status': order_status,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders_list,
        'today': today,
        'week_ago': week_ago,
        'month_ago': month_ago,
    }
    
    return render(request, 'admin/sales_dashboard.html', context)

@staff_member_required
def inventory_management(request):
    """Inventory management page for admin users."""
    
    # All products with inventory info
    products = Product.objects.filter(track_inventory=True).annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('name')
    
    # Out of stock products
    out_of_stock = products.filter(stock_quantity=0)
    
    # Low stock products
    low_stock = products.filter(stock_quantity__lt=10, stock_quantity__gt=0)
    
    # High stock products
    high_stock = products.filter(stock_quantity__gt=100)
    
    context = {
        'products': products,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'high_stock': high_stock,
    }
    
    return render(request, 'admin/inventory_management.html', context)

@staff_member_required
def customer_analytics(request):
    """Customer analytics and management page."""
    
    # Customer statistics
    total_customers = User.objects.filter(is_active=True).count()
    new_customers_this_month = User.objects.filter(
        date_joined__gte=timezone.now().replace(day=1)
    ).count()
    
    # Top customers by order count
    top_customers = User.objects.annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).filter(order_count__gt=0).order_by('-total_spent')[:10]
    
    # Customer registration trends (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_registrations = []
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        count = User.objects.filter(date_joined__date=date.date()).count()
        daily_registrations.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Customer activity
    active_customers = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    context = {
        'total_customers': total_customers,
        'new_customers_this_month': new_customers_this_month,
        'top_customers': top_customers,
        'daily_registrations': daily_registrations,
        'active_customers': active_customers,
    }
    
    return render(request, 'admin/customer_analytics.html', context)

@staff_member_required
def product_analytics(request):
    """Product analytics and performance page."""
    
    # Product performance metrics
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    featured_products = Product.objects.filter(is_featured=True).count()
    
    # Best performing products
    best_sellers = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity'),
        total_revenue=Sum(F('orderitem__quantity') * F('orderitem__price'))
    ).filter(total_sold__gt=0).order_by('-total_revenue')[:10]
    
    # Category performance
    category_performance = Category.objects.annotate(
        product_count=Count('products'),
        total_sold=Sum('products__orderitem__quantity'),
        total_revenue=Sum(F('products__orderitem__quantity') * F('products__orderitem__price'))
    ).filter(product_count__gt=0).order_by('-total_revenue')
    
    # Product status distribution
    status_distribution = {
        'active': Product.objects.filter(is_active=True).count(),
        'inactive': Product.objects.filter(is_active=False).count(),
        'featured': Product.objects.filter(is_featured=True).count(),
        'low_stock': Product.objects.filter(stock_quantity__lt=10, track_inventory=True).count(),
        'out_of_stock': Product.objects.filter(stock_quantity=0, track_inventory=True).count(),
    }
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'category_performance': category_performance,
        'status_distribution': status_distribution,
    }
    
    return render(request, 'admin/product_analytics.html', context)

@staff_member_required
def order_analytics(request):
    """Order analytics and management page."""
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    
    # Revenue metrics
    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Average order value
    avg_order_value = Order.objects.aggregate(
        avg=Avg('total_amount')
    )['avg'] or 0
    
    # Order trends (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_orders = []
    daily_revenue = []
    
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        orders_count = Order.objects.filter(created_at__date=date.date()).count()
        revenue = Order.objects.filter(created_at__date=date.date()).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        daily_orders.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': orders_count
        })
        daily_revenue.append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': float(revenue)
        })
    
    # Order status distribution
    status_distribution = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'daily_orders': daily_orders,
        'daily_revenue': daily_revenue,
        'status_distribution': status_distribution,
    }
    
    return render(request, 'admin/order_analytics.html', context)

@staff_member_required
def bulk_operations(request):
    """Bulk operations management page."""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'bulk_restock':
            product_ids = request.POST.getlist('product_ids')
            restock_quantity = int(request.POST.get('restock_quantity', 100))
            
            updated = Product.objects.filter(id__in=product_ids).update(
                stock_quantity=restock_quantity
            )
            messages.success(request, f'{updated} products were restocked to {restock_quantity} units.')
            
        elif action == 'bulk_activate':
            product_ids = request.POST.getlist('product_ids')
            updated = Product.objects.filter(id__in=product_ids).update(is_active=True)
            messages.success(request, f'{updated} products were activated.')
            
        elif action == 'bulk_deactivate':
            product_ids = request.POST.getlist('product_ids')
            updated = Product.objects.filter(id__in=product_ids).update(is_active=False)
            messages.success(request, f'{updated} products were deactivated.')
            
        elif action == 'bulk_feature':
            product_ids = request.POST.getlist('product_ids')
            updated = Product.objects.filter(id__in=product_ids).update(is_featured=True)
            messages.success(request, f'{updated} products were marked as featured.')
            
        return redirect('admin_bulk_operations')
    
    # Get products for bulk operations
    products = Product.objects.all().order_by('name')
    
    context = {
        'products': products,
    }
    
    return render(request, 'admin/bulk_operations.html', context)

@staff_member_required
def export_data(request):
    """Export data functionality."""
    export_type = request.GET.get('type', 'products')
    
    if export_type == 'products':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Name', 'SKU', 'Category', 'Price', 'Compare Price', 'Stock', 
            'Active', 'Featured', 'Created At'
        ])
        
        for product in Product.objects.all():
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
    
    elif export_type == 'orders':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Customer', 'Status', 'Payment Status', 'Total Amount',
            'Items Count', 'Created At', 'Tracking Number'
        ])
        
        for order in Order.objects.all():
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
    
    elif export_type == 'customers':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Username', 'Email', 'First Name', 'Last Name', 'Date Joined', 
            'Last Login', 'Is Active', 'Order Count', 'Total Spent'
        ])
        
        for user in User.objects.annotate(
            order_count=Count('orders'),
            total_spent=Sum('orders__total_amount')
        ):
            writer.writerow([
                user.username,
                user.email,
                user.first_name,
                user.last_name,
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
                user.is_active,
                user.order_count,
                user.total_spent or 0
            ])
        
        return response
    
    return JsonResponse({'error': 'Invalid export type'}, status=400)
