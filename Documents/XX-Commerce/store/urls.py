from django.urls import path
from . import views
from . import cart_views
from . import wishlist_views
from . import admin_views

app_name = 'store'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:category_slug>/', views.product_list, name='category_detail'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', cart_views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', cart_views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', cart_views.remove_from_cart, name='remove_from_cart'),
    path('apply-coupon/', cart_views.apply_coupon, name='apply_coupon'),
    
    # Checkout and Orders
    path('checkout/', cart_views.checkout, name='checkout'),
    path('orders/', cart_views.order_list, name='order_list'),
    path('orders/<str:order_number>/', cart_views.order_detail, name='order_detail'),
    
    # Wishlist
    path('wishlist/', wishlist_views.wishlist, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', wishlist_views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', wishlist_views.remove_from_wishlist, name='remove_from_wishlist'),
    
]
