from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from decimal import Decimal

from .models import Cart, CartItem, Order, OrderItem, Address, Coupon, Wishlist
from .forms import AddToCartForm, CheckoutForm, CouponForm


@require_POST
def add_to_cart(request, product_id):
    """Add product to cart."""
    from .models import Product
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    form = AddToCartForm(request.POST)
    
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        
        # Get or create cart
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
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_items': cart.total_items,
                'cart_total': str(cart.total_price)
            })
        else:
            return redirect('store:product_detail', slug=product.slug)
    else:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'message': 'Invalid quantity'
            })
        else:
            messages.error(request, 'Invalid quantity')
            return redirect('store:product_detail', slug=product.slug)


@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Check if user owns this cart item
    if request.user.is_authenticated:
        if cart_item.cart.user != request.user:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})
    else:
        if cart_item.cart.session_key != request.session.session_key:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        message = 'Item removed from cart'
    else:
        cart_item.quantity = quantity
        cart_item.save()
        message = 'Cart updated'
    
    cart = cart_item.cart
    
    return JsonResponse({
        'success': True,
        'message': message,
        'cart_items': cart.total_items,
        'cart_total': str(cart.total_price),
        'item_total': str(cart_item.line_total)
    })


@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Check if user owns this cart item
    if request.user.is_authenticated:
        if cart_item.cart.user != request.user:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})
    else:
        if cart_item.cart.session_key != request.session.session_key:
            return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    product_name = cart_item.product.name
    cart_item.delete()
    
    cart = cart_item.cart
    
    return JsonResponse({
        'success': True,
        'message': f'{product_name} removed from cart',
        'cart_items': cart.total_items,
        'cart_total': str(cart.total_price)
    })


@login_required
def checkout(request):
    """Checkout page."""
    cart = get_object_or_404(Cart, user=request.user, is_active=True)
    cart_items = cart.items.select_related('product').all()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('store:cart')
    
    # Get user's addresses
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = cart.total_price
            order.total_amount = cart.total_price  # Add tax, shipping, discount logic
            order.save()
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku
                )
                
                # Reduce stock
                cart_item.product.reduce_stock(cart_item.quantity)
            
            # Deactivate cart
            cart.is_active = False
            cart.save()
            
            messages.success(request, f'Order {order.order_number} created successfully!')
            return redirect('store:order_detail', order_number=order.order_number)
    else:
        form = CheckoutForm(user=request.user)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'form': form,
        'addresses': addresses,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_list(request):
    """User's order history."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Order detail page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.select_related('product').all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/order_detail.html', context)


@require_POST
def apply_coupon(request):
    """Apply coupon to cart."""
    form = CouponForm(request.POST)
    
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            
            # Get cart
            if request.user.is_authenticated:
                cart = Cart.objects.get(user=request.user, is_active=True)
            else:
                session_key = request.session.session_key
                cart = Cart.objects.get(session_key=session_key, is_active=True)
            
            # Check if coupon is valid
            if coupon.is_valid(cart_total=cart.total_price):
                # Store coupon in session
                request.session['coupon_code'] = code
                messages.success(request, f'Coupon {code} applied successfully!')
            else:
                messages.error(request, 'Coupon is not valid for this order.')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
    else:
        messages.error(request, 'Please enter a valid coupon code.')
    
    return redirect('store:cart')
