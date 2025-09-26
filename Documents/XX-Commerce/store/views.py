from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from decimal import Decimal
import json

from .models import (
    Category, Product, ProductImage, Cart, CartItem, 
    Order, OrderItem, Address, Coupon, Wishlist
)
from .forms import AddToCartForm, CheckoutForm, CouponForm, UserRegistrationForm, AddressForm


def home(request):
    """Home page with featured products and categories."""
    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('category').prefetch_related('images')[:8]
    
    categories = Category.objects.filter(
        is_active=True, 
        parent__isnull=True
    )[:6]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list(request, category_slug=None):
    """Product listing page with filtering and pagination."""
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    
    # Filter by category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)
        # Include subcategories
        subcategories = category.children.filter(is_active=True)
        products = products.filter(
            Q(category=category) | Q(category__in=subcategories)
        )
    else:
        category = None
        subcategories = None
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Filter by availability
    in_stock = request.GET.get('in_stock')
    if in_stock:
        products = products.filter(stock_quantity__gt=0)
    
    # Sorting
    sort_by = request.GET.get('sort', 'created_at')
    sort_options = {
        'created_at': '-created_at',
        'name': 'name',
        'price_asc': 'price',
        'price_desc': '-price',
        'popularity': '-created_at',  # Could be based on order count
    }
    if sort_by in sort_options:
        products = products.order_by(sort_options[sort_by])
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'category': category,
        'subcategories': subcategories,
        'search_query': search_query,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """Product detail page."""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        slug=slug, 
        is_active=True
    )
    
    # Get related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Add to cart form
    add_to_cart_form = AddToCartForm()
    
    # Check if product is in user's wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user, 
            product=product
        ).exists()
    
    context = {
        'product': product,
        'related_products': related_products,
        'add_to_cart_form': add_to_cart_form,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'store/product_detail.html', context)


def cart_view(request):
    """Shopping cart page."""
    if request.user.is_authenticated:
        # First try to get existing active cart
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if not cart:
            # If no active cart exists, create a new one
            cart = Cart.objects.create(user=request.user, is_active=True)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        # First try to get existing active cart
        cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
        if not cart:
            # If no active cart exists, create a new one
            cart = Cart.objects.create(session_key=session_key, is_active=True)
    
    cart_items = cart.items.select_related('product').all()
    
    # Coupon form
    coupon_form = CouponForm()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'coupon_form': coupon_form,
    }
    return render(request, 'store/cart.html', context)


def category_list(request):
    """Category listing page."""
    categories = Category.objects.filter(
        is_active=True, 
        parent__isnull=True
    ).prefetch_related('children')
    
    context = {
        'categories': categories,
    }
    return render(request, 'store/category_list.html', context)


# Authentication views
def register(request):
    """User registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'registration/register.html', context)


@login_required
def profile(request):
    """User profile page."""
    user = request.user
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'recent_orders': recent_orders,
    }
    return render(request, 'store/profile.html', context)


@login_required
def address_list(request):
    """User's address list."""
    addresses = Address.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses,
    }
    return render(request, 'store/address_list.html', context)


@login_required
def address_create(request):
    """Create new address."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address created successfully!')
            return redirect('address_list')
    else:
        form = AddressForm()
    
    context = {
        'form': form,
    }
    return render(request, 'store/address_form.html', context)


@login_required
def address_edit(request, pk):
    """Edit address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address,
    }
    return render(request, 'store/address_form.html', context)


@login_required
def address_delete(request, pk):
    """Delete address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('address_list')
    
    context = {
        'address': address,
    }
    return render(request, 'store/address_confirm_delete.html', context)