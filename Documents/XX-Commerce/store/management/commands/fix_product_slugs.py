from django.core.management.base import BaseCommand
from store.models import Product
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Fix products with empty or invalid slugs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find products with empty or None slugs
        products_with_empty_slugs = Product.objects.filter(slug__in=['', None])
        
        if not products_with_empty_slugs.exists():
            self.stdout.write(self.style.SUCCESS('No products with empty slugs found.'))
            return
        
        self.stdout.write(f'Found {products_with_empty_slugs.count()} products with empty slugs:')
        
        for product in products_with_empty_slugs:
            old_slug = product.slug or '(empty)'
            new_slug = slugify(product.name)
            
            # Ensure slug is unique
            counter = 1
            original_slug = new_slug
            while Product.objects.filter(slug=new_slug).exclude(id=product.id).exists():
                new_slug = f"{original_slug}-{counter}"
                counter += 1
            
            self.stdout.write(f'  - {product.name}: "{old_slug}" -> "{new_slug}"')
            
            if not dry_run:
                product.slug = new_slug
                product.save()
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run completed. Use without --dry-run to apply changes.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully fixed {products_with_empty_slugs.count()} product slugs.'))
