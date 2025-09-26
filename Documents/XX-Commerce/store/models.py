from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class TimeStampedModel(models.Model):
    """Abstract base class with created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """Product categories for organizing products."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:category_detail', kwargs={'slug': self.slug})


class Product(TimeStampedModel):
    """Main product model with inventory management."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                      validators=[MinValueValidator(Decimal('0.01'))])
    
    # Inventory
    sku = models.CharField(max_length=50, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    allow_backorder = models.BooleanField(default=False)
    
    # Product details
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['price']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0

    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_price exists."""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0

    def reduce_stock(self, quantity):
        """Reduce stock quantity."""
        if self.track_inventory:
            if self.stock_quantity >= quantity:
                self.stock_quantity -= quantity
                self.save(update_fields=['stock_quantity'])
                return True
            elif self.allow_backorder:
                self.stock_quantity -= quantity
                self.save(update_fields=['stock_quantity'])
                return True
            return False
        return True

    @property
    def primary_image(self):
        """Get the primary image for this product."""
        try:
            return self.images.filter(is_primary=True).first()
        except:
            return None


class ProductImage(TimeStampedModel):
    """Product images with ordering."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
            models.Index(fields=['product', 'sort_order']),
        ]

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class Address(TimeStampedModel):
    """Customer addresses for shipping and billing."""
    ADDRESS_TYPES = [
        ('shipping', 'Shipping'),
        ('billing', 'Billing'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company = models.CharField(max_length=100, blank=True)
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    phone = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'address_type']),
            models.Index(fields=['user', 'is_default']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.address_line_1}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per type per user
        if self.is_default:
            Address.objects.filter(
                user=self.user, 
                address_type=self.address_type, 
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)


class Cart(TimeStampedModel):
    """Shopping cart for users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart {self.session_key}"

    @property
    def total_items(self):
        """Get total number of items in cart."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def total_price(self):
        """Calculate total price of all items in cart."""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.line_total
        return total

    @staticmethod
    def get_or_create_cart(user=None, session_key=None):
        """Get existing cart or create new one."""
        if user and user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=user, 
                is_active=True,
                defaults={'session_key': ''}
            )
        else:
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                is_active=True,
                defaults={'user': None}
            )
        return cart


class CartItem(TimeStampedModel):
    """Individual items in shopping cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ['cart', 'product']
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def line_total(self):
        """Calculate total price for this line item."""
        return self.product.price * self.quantity

    def clean(self):
        """Validate cart item."""
        from django.core.exceptions import ValidationError
        if not self.product.is_in_stock and not self.product.allow_backorder:
            raise ValidationError("Product is out of stock")
        if self.quantity > self.product.stock_quantity and not self.product.allow_backorder:
            raise ValidationError("Not enough stock available")


class Order(TimeStampedModel):
    """Customer orders."""
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Order status
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Addresses
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='shipping_orders')
    billing_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='billing_orders')
    
    # Additional info
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate unique order number."""
        import random
        import string
        while True:
            order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not Order.objects.filter(order_number=order_number).exists():
                return order_number

    @property
    def total_items(self):
        """Get total number of items in order."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def update_status(self, new_status):
        """Update order status with timestamp."""
        self.status = new_status
        if new_status == 'shipped':
            self.shipped_at = timezone.now()
        elif new_status == 'delivered':
            self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'shipped_at', 'delivered_at'])


class OrderItem(TimeStampedModel):
    """Individual items in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    product_name = models.CharField(max_length=200)  # Snapshot of product name
    product_sku = models.CharField(max_length=50)  # Snapshot of product SKU

    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def line_total(self):
        """Calculate total price for this line item."""
        return self.price * self.quantity


class Coupon(TimeStampedModel):
    """Discount coupons."""
    COUPON_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200)
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]

    def __str__(self):
        return f"{self.code} - {self.description}"

    def is_valid(self, user=None, cart_total=None):
        """Check if coupon is valid for use."""
        now = timezone.now()
        if not self.is_active:
            return False
        if not (self.valid_from <= now <= self.valid_until):
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        if cart_total and self.minimum_amount and cart_total < self.minimum_amount:
            return False
        return True

    def calculate_discount(self, cart_total):
        """Calculate discount amount for given cart total."""
        if not self.is_valid(cart_total=cart_total):
            return Decimal('0.00')
        
        if self.coupon_type == 'percentage':
            discount = cart_total * (self.value / 100)
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:  # fixed
            discount = self.value
        
        return min(discount, cart_total)


class Wishlist(TimeStampedModel):
    """User wishlist for saving favorite products."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')

    class Meta:
        unique_together = ['user', 'product']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"