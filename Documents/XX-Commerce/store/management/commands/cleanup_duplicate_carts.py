from django.core.management.base import BaseCommand
from store.models import Cart

class Command(BaseCommand):
    help = 'Clean up duplicate active carts for users'

    def handle(self, *args, **kwargs):
        # Find users with multiple active carts
        from django.db.models import Count
        
        # For authenticated users
        user_carts = Cart.objects.filter(
            user__isnull=False, 
            is_active=True
        ).values('user').annotate(
            cart_count=Count('id')
        ).filter(cart_count__gt=1)
        
        cleaned_count = 0
        
        for cart_data in user_carts:
            user_id = cart_data['user']
            user_carts_queryset = Cart.objects.filter(
                user_id=user_id, 
                is_active=True
            ).order_by('-created_at')
            
            # Keep the most recent cart, deactivate others
            latest_cart = user_carts_queryset.first()
            duplicate_carts = user_carts_queryset.exclude(id=latest_cart.id)
            
            deactivated_count = duplicate_carts.update(is_active=False)
            cleaned_count += deactivated_count
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'User {user_id}: Kept cart {latest_cart.id}, '
                    f'deactivated {deactivated_count} duplicate carts'
                )
            )
        
        # For anonymous users (session-based carts)
        session_carts = Cart.objects.filter(
            session_key__isnull=False, 
            is_active=True
        ).values('session_key').annotate(
            cart_count=Count('id')
        ).filter(cart_count__gt=1)
        
        for cart_data in session_carts:
            session_key = cart_data['session_key']
            session_carts_queryset = Cart.objects.filter(
                session_key=session_key, 
                is_active=True
            ).order_by('-created_at')
            
            # Keep the most recent cart, deactivate others
            latest_cart = session_carts_queryset.first()
            duplicate_carts = session_carts_queryset.exclude(id=latest_cart.id)
            
            deactivated_count = duplicate_carts.update(is_active=False)
            cleaned_count += deactivated_count
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Session {session_key}: Kept cart {latest_cart.id}, '
                    f'deactivated {deactivated_count} duplicate carts'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned up {cleaned_count} duplicate carts!'
            )
        )
