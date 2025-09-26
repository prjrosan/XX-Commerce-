from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Product, Wishlist


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        message = f'{product.name} added to wishlist!'
    else:
        message = f'{product.name} is already in your wishlist!'
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({
            'success': True,
            'message': message,
            'in_wishlist': True
        })
    
    messages.info(request, message)
    return redirect('store:product_detail', slug=product.slug)


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        message = f'{product.name} removed from wishlist!'
    except Wishlist.DoesNotExist:
        message = f'{product.name} was not in your wishlist!'
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({
            'success': True,
            'message': message,
            'in_wishlist': False
        })
    
    messages.info(request, message)
    return redirect('store:product_detail', slug=product.slug)


@login_required
def wishlist(request):
    """User's wishlist page."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/wishlist.html', context)
