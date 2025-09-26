# Database Entity Relationship Diagram

## Core Entities and Relationships

```
User (Django Auth)
├── Address (1:N) - Shipping/Billing addresses
├── Cart (1:N) - Shopping carts
├── Order (1:N) - Customer orders
└── Wishlist (1:N) - Saved products

Category
├── Category (1:N) - Self-referencing for subcategories
└── Product (1:N) - Products in category

Product
├── ProductImage (1:N) - Product images
├── CartItem (1:N) - Items in carts
├── OrderItem (1:N) - Items in orders
└── Wishlist (1:N) - User wishlists

Cart
└── CartItem (1:N) - Items in cart

Order
├── OrderItem (1:N) - Items in order
├── Address (1:1) - Shipping address
└── Address (1:1) - Billing address

Coupon
└── (Used in orders via session/code)
```

## Key Foreign Key Constraints

1. **Product → Category**: `category_id` (CASCADE on delete)
2. **OrderItem → Order**: `order_id` (CASCADE on delete)
3. **OrderItem → Product**: `product_id` (PROTECT on delete)
4. **CartItem → Cart**: `cart_id` (CASCADE on delete)
5. **CartItem → Product**: `product_id` (CASCADE on delete)
6. **Address → User**: `user_id` (CASCADE on delete)
7. **Order → User**: `user_id` (CASCADE on delete)
8. **Order → Address**: `shipping_address_id` (PROTECT on delete)
9. **Order → Address**: `billing_address_id` (PROTECT on delete)
10. **Wishlist → User**: `user_id` (CASCADE on delete)
11. **Wishlist → Product**: `product_id` (CASCADE on delete)

## Database Indexes

### Product Table
- `name` - For product search
- `slug` - For URL lookups
- `category_id` - For category filtering
- `is_active` - For active product filtering
- `is_featured` - For featured product queries
- `price` - For price sorting/filtering
- `sku` - For SKU lookups

### Order Table
- `user_id + created_at` - For user order history
- `order_number` - For order lookups
- `status` - For status filtering
- `payment_status` - For payment filtering
- `created_at` - For date-based queries

### Category Table
- `name` - For category search
- `slug` - For URL lookups
- `is_active` - For active category filtering

### Cart Table
- `user_id` - For user cart lookup
- `session_key` - For anonymous cart lookup
- `is_active` - For active cart filtering

### Address Table
- `user_id + address_type` - For user address filtering
- `user_id + is_default` - For default address lookup
