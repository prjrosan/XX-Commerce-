from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models
from store.models import Cart
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix duplicate active carts for users and sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Fixing duplicate active carts...')
        
        # Fix authenticated user carts
        users_with_duplicates = User.objects.annotate(
            active_cart_count=models.Count('carts', filter=models.Q(carts__is_active=True))
        ).filter(active_cart_count__gt=1)
        
        fixed_users = 0
        for user in users_with_duplicates:
            active_carts = Cart.objects.filter(user=user, is_active=True).order_by('-created_at')
            if active_carts.count() > 1:
                latest_cart = active_carts.first()
                duplicate_carts = active_carts.exclude(id=latest_cart.id)
                
                if dry_run:
                    self.stdout.write(
                        f'Would fix user {user.username}: '
                        f'{duplicate_carts.count()} duplicate carts, '
                        f'keeping cart {latest_cart.id}'
                    )
                else:
                    duplicate_carts.update(is_active=False)
                    self.stdout.write(
                        f'Fixed user {user.username}: '
                        f'deactivated {duplicate_carts.count()} duplicate carts'
                    )
                fixed_users += 1
        
        # Fix session carts
        session_duplicates = Cart.objects.filter(
            session_key__isnull=False,
            user__isnull=True,
            is_active=True
        ).values('session_key').annotate(
            cart_count=models.Count('id')
        ).filter(cart_count__gt=1)
        
        fixed_sessions = 0
        for session_data in session_duplicates:
            session_key = session_data['session_key']
            active_carts = Cart.objects.filter(
                session_key=session_key, 
                user__isnull=True, 
                is_active=True
            ).order_by('-created_at')
            
            if active_carts.count() > 1:
                latest_cart = active_carts.first()
                duplicate_carts = active_carts.exclude(id=latest_cart.id)
                
                if dry_run:
                    self.stdout.write(
                        f'Would fix session {session_key}: '
                        f'{duplicate_carts.count()} duplicate carts, '
                        f'keeping cart {latest_cart.id}'
                    )
                else:
                    duplicate_carts.update(is_active=False)
                    self.stdout.write(
                        f'Fixed session {session_key}: '
                        f'deactivated {duplicate_carts.count()} duplicate carts'
                    )
                fixed_sessions += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would fix {fixed_users} users and {fixed_sessions} sessions'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully fixed {fixed_users} users and {fixed_sessions} sessions'
                )
            )
