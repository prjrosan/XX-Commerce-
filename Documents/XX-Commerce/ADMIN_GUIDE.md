# XX Commerce Admin Guide

## How to Access the Admin Panel

1. **Start the server:**
   ```bash
   python3 manage.py runserver 8000
   ```

2. **Access the admin panel:**
   - Go to: `http://127.0.0.1:8000/admin/`
   - Login with one of these accounts:
     - Username: `admin` | Email: `admin@xxcommerce.com`
     - Username: `praja` | Email: `praja@xxcommerce.com`

## Product Management Features

### 1. **Edit Product Prices (Quick Edit)**
- Go to **Products** section
- You can edit prices directly in the list view:
  - **Price**: Main product price
  - **Compare Price**: Original price (for showing discounts)
  - **Stock Quantity**: Available inventory
  - **Active**: Show/hide product
  - **Featured**: Mark as featured product

### 2. **Add New Products**
- Click **"Add Product"** button
- Fill in the required fields:
  - **Name**: Product name
  - **Category**: Select from existing categories
  - **Price**: Product price in JPY
  - **Compare Price**: Original price (optional)
  - **Stock Quantity**: Available inventory
  - **Description**: Product details
  - **Images**: Upload product images

### 3. **Bulk Actions**
- Select multiple products using checkboxes
- Choose from dropdown actions:
  - **Mark selected products as active**
  - **Mark selected products as inactive**
  - **Mark selected products as featured**
  - **Mark selected products as unfeatured**

### 4. **Product Images**
- Add multiple images per product
- Set primary image
- Reorder images by sort order
- Add alt text for accessibility

### 5. **Category Management**
- Create new categories
- Set parent categories for subcategories
- Enable/disable categories
- Auto-generate SEO-friendly URLs

## Key Features

### ✅ **Price Management**
- Edit prices directly from product list
- Set both regular and compare prices
- Bulk price updates (coming soon)

### ✅ **Inventory Control**
- Track stock quantities
- Enable/disable inventory tracking
- Allow backorders for out-of-stock items

### ✅ **Product Status**
- Activate/deactivate products
- Mark products as featured
- Control product visibility

### ✅ **SEO Optimization**
- Auto-generate URLs from product names
- Set meta titles and descriptions
- Optimize for search engines

## Quick Start Checklist

1. ✅ **Login to admin panel**
2. ✅ **Go to Products section**
3. ✅ **Edit existing product prices** (click on price field)
4. ✅ **Add new products** (click "Add Product")
5. ✅ **Upload product images**
6. ✅ **Set product status** (active/featured)
7. ✅ **Manage categories**

## Tips for Success

- **Always set compare prices** to show discounts
- **Upload high-quality images** for better presentation
- **Use descriptive product names** for SEO
- **Set appropriate stock quantities** to avoid overselling
- **Mark popular products as featured** to highlight them

## Support

If you need help with the admin panel, check:
- Product documentation in the admin interface
- Django admin documentation
- Contact the development team

---

**Happy managing your e-commerce store!** 🛍️
