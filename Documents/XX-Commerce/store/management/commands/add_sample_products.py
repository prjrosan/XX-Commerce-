from django.core.management.base import BaseCommand
from store.models import Product, Category
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add sample products to the store'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of products to add'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Category name to add products to'
        )

    def handle(self, *args, **options):
        count = options['count']
        category_name = options.get('category', 'Electronics')
        
        # Get or create category
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={
                'slug': category_name.lower().replace(' ', '-'),
                'description': f'Sample {category_name} products'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created category: {category_name}')
            )
        
        # Sample product data
        sample_products = [
            {
                'name': 'Wireless Bluetooth Headphones',
                'sku': 'WBH-001',
                'price': Decimal('99.99'),
                'description': 'High-quality wireless headphones with noise cancellation',
                'short_description': 'Premium wireless headphones'
            },
            {
                'name': 'Smart Watch Series 5',
                'sku': 'SWS-005',
                'price': Decimal('299.99'),
                'description': 'Advanced smartwatch with health monitoring features',
                'short_description': 'Latest smartwatch with health tracking'
            },
            {
                'name': 'USB-C Charging Cable',
                'sku': 'UCC-001',
                'price': Decimal('19.99'),
                'description': 'Fast charging USB-C cable, 6 feet long',
                'short_description': 'Fast charging USB-C cable'
            },
            {
                'name': 'Wireless Mouse',
                'sku': 'WM-001',
                'price': Decimal('39.99'),
                'description': 'Ergonomic wireless mouse with precision tracking',
                'short_description': 'Ergonomic wireless mouse'
            },
            {
                'name': 'Mechanical Keyboard',
                'sku': 'MK-001',
                'price': Decimal('149.99'),
                'description': 'RGB mechanical keyboard with blue switches',
                'short_description': 'RGB mechanical keyboard'
            }
        ]
        
        products_added = 0
        
        for i, product_data in enumerate(sample_products[:count]):
            # Create unique SKU if product already exists
            base_sku = product_data['sku']
            sku = base_sku
            counter = 1
            while Product.objects.filter(sku=sku).exists():
                sku = f"{base_sku}-{counter:03d}"
                counter += 1
            
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': product_data['name'],
                    'slug': f"{product_data['name'].lower().replace(' ', '-')}-{sku.lower()}",
                    'category': category,
                    'price': product_data['price'],
                    'description': product_data['description'],
                    'short_description': product_data['short_description'],
                    'stock_quantity': 100,  # Start with 100 units
                    'is_active': True,
                    'track_inventory': True
                }
            )
            
            if created:
                products_added += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created product: {product.name} (SKU: {product.sku})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Product already exists: {product.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {products_added} new products!')
        )
