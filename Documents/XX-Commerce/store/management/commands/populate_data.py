from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from store.models import Category, Product, ProductImage, Coupon


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create categories
        electronics = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic devices and accessories',
            is_active=True
        )

        clothing = Category.objects.create(
            name='Clothing',
            slug='clothing',
            description='Fashion and apparel',
            is_active=True
        )

        home_garden = Category.objects.create(
            name='Home & Garden',
            slug='home-garden',
            description='Home improvement and garden supplies',
            is_active=True
        )

        books = Category.objects.create(
            name='Books',
            slug='books',
            description='Books and educational materials',
            is_active=True
        )

        # Create subcategories
        smartphones = Category.objects.create(
            name='Smartphones',
            slug='smartphones',
            description='Mobile phones and accessories',
            parent=electronics,
            is_active=True
        )

        laptops = Category.objects.create(
            name='Laptops',
            slug='laptops',
            description='Laptop computers and accessories',
            parent=electronics,
            is_active=True
        )

        # Create products
        products_data = [
            {
                'name': 'iPhone 15 Pro',
                'slug': 'iphone-15-pro',
                'description': 'The latest iPhone with advanced features and premium design.',
                'short_description': 'Latest iPhone with Pro features',
                'category': smartphones,
                'price': Decimal('999.99'),
                'compare_price': Decimal('1099.99'),
                'sku': 'IPH15PRO001',
                'stock_quantity': 50,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'MacBook Pro 16"',
                'slug': 'macbook-pro-16',
                'description': 'Powerful laptop for professionals with M3 chip.',
                'short_description': 'Professional laptop with M3 chip',
                'category': laptops,
                'price': Decimal('2499.99'),
                'compare_price': Decimal('2799.99'),
                'sku': 'MBP16M3001',
                'stock_quantity': 25,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Samsung Galaxy S24',
                'slug': 'samsung-galaxy-s24',
                'description': 'Android flagship smartphone with excellent camera.',
                'short_description': 'Android flagship with great camera',
                'category': smartphones,
                'price': Decimal('799.99'),
                'compare_price': Decimal('899.99'),
                'sku': 'SGS24001',
                'stock_quantity': 75,
                'is_active': True,
                'is_featured': False,
            },
            {
                'name': 'Dell XPS 13',
                'slug': 'dell-xps-13',
                'description': 'Ultrabook with stunning display and long battery life.',
                'short_description': 'Ultrabook with great display',
                'category': laptops,
                'price': Decimal('1299.99'),
                'sku': 'DXP13001',
                'stock_quantity': 30,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Nike Air Max 270',
                'slug': 'nike-air-max-270',
                'description': 'Comfortable running shoes with modern design.',
                'short_description': 'Comfortable running shoes',
                'category': clothing,
                'price': Decimal('150.00'),
                'sku': 'NAM27001',
                'stock_quantity': 100,
                'is_active': True,
                'is_featured': False,
            },
            {
                'name': 'Adidas Ultraboost 22',
                'slug': 'adidas-ultraboost-22',
                'description': 'High-performance running shoes with Boost technology.',
                'short_description': 'High-performance running shoes',
                'category': clothing,
                'price': Decimal('180.00'),
                'sku': 'AUB22001',
                'stock_quantity': 80,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Garden Hose 50ft',
                'slug': 'garden-hose-50ft',
                'description': 'Heavy-duty garden hose for all your watering needs.',
                'short_description': 'Heavy-duty garden hose',
                'category': home_garden,
                'price': Decimal('29.99'),
                'sku': 'GH50001',
                'stock_quantity': 200,
                'is_active': True,
                'is_featured': False,
            },
            {
                'name': 'Python Programming Book',
                'slug': 'python-programming-book',
                'description': 'Complete guide to Python programming for beginners.',
                'short_description': 'Complete Python programming guide',
                'category': books,
                'price': Decimal('49.99'),
                'sku': 'PPB001',
                'stock_quantity': 150,
                'is_active': True,
                'is_featured': False,
            },
        ]

        for product_data in products_data:
            product = Product.objects.create(**product_data)
            
            # Create product image
            image_filename = product.name.lower().replace(' ', '-').replace('&', 'and') + '.jpg'
            image_path = f'products/{image_filename}'
            
            # Create ProductImage
            ProductImage.objects.create(
                product=product,
                image=image_path,
                alt_text=f'{product.name} product image',
                is_primary=True,
                sort_order=0
            )
            
            self.stdout.write(f'Created product: {product.name} with image')

        # Create coupons
        now = timezone.now()
        coupons_data = [
            {
                'code': 'WELCOME10',
                'description': 'Welcome discount for new customers',
                'coupon_type': 'percentage',
                'value': Decimal('10.00'),
                'minimum_amount': Decimal('50.00'),
                'usage_limit': 1000,
                'valid_from': now,
                'valid_until': now + timezone.timedelta(days=365),
                'is_active': True,
            },
            {
                'code': 'SAVE20',
                'description': 'Save $20 on orders over $100',
                'coupon_type': 'fixed',
                'value': Decimal('20.00'),
                'minimum_amount': Decimal('100.00'),
                'usage_limit': 500,
                'valid_from': now,
                'valid_until': now + timezone.timedelta(days=180),
                'is_active': True,
            },
        ]

        for coupon_data in coupons_data:
            coupon = Coupon.objects.create(**coupon_data)
            self.stdout.write(f'Created coupon: {coupon.code}')

        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@xxcommerce.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write('Created superuser: admin/admin123')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
