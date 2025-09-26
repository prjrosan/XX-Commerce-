from django.core.management.base import BaseCommand
from django.db import transaction
from store.models import Cart, CartItem


class Command(BaseCommand):
    help = 'Clean up duplicate active carts'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Find users with multiple active carts
            from django.contrib.auth.models import User
            
            # Clean up user carts
            for user in User.objects.all():
                active_carts = Cart.objects.filter(user=user, is_active=True).order_by('created_at')
                if active_carts.count() > 1:
                    self.stdout.write(f'Found {active_carts.count()} active carts for user {user.username}')
                    
                    # Keep the first cart, merge others into it
                    main_cart = active_carts.first()
                    other_carts = active_carts[1:]
                    
                    for cart in other_carts:
                        # Move cart items to main cart
                        for item in cart.items.all():
                            existing_item = main_cart.items.filter(product=item.product).first()
                            if existing_item:
                                existing_item.quantity += item.quantity
                                existing_item.save()
                            else:
                                item.cart = main_cart
                                item.save()
                        
                        # Deactivate the duplicate cart
                        cart.is_active = False
                        cart.save()
                        self.stdout.write(f'  Merged cart {cart.id} into {main_cart.id}')
            
            # Clean up session carts
            session_carts = Cart.objects.filter(session_key__isnull=False, is_active=True)
            session_keys = session_carts.values_list('session_key', flat=True).distinct()
            
            for session_key in session_keys:
                if session_key:
                    active_carts = Cart.objects.filter(session_key=session_key, is_active=True).order_by('created_at')
                    if active_carts.count() > 1:
                        self.stdout.write(f'Found {active_carts.count()} active carts for session {session_key}')
                        
                        # Keep the first cart, merge others into it
                        main_cart = active_carts.first()
                        other_carts = active_carts[1:]
                        
                        for cart in other_carts:
                            # Move cart items to main cart
                            for item in cart.items.all():
                                existing_item = main_cart.items.filter(product=item.product).first()
                                if existing_item:
                                    existing_item.quantity += item.quantity
                                    existing_item.save()
                                else:
                                    item.cart = main_cart
                                    item.save()
                            
                            # Deactivate the duplicate cart
                            cart.is_active = False
                            cart.save()
                            self.stdout.write(f'  Merged cart {cart.id} into {main_cart.id}')
        
        self.stdout.write(self.style.SUCCESS('Cart cleanup completed successfully!'))
