from .models import Cart, Category


def cart(request):
    """Add cart information to template context."""
    cart = None
    cart_items = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
            if cart:
                cart_items = cart.total_items
                cart_total = cart.total_price
        except Exception:
            pass
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
                if cart:
                    cart_items = cart.total_items
                    cart_total = cart.total_price
            except Exception:
                pass
    
    return {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }


def categories(request):
    """Add categories to template context."""
    try:
        categories = Category.objects.filter(
            is_active=True, 
            parent__isnull=True
        )[:6]
    except Exception as e:
        categories = []
    
    return {
        'categories': categories,
    }
