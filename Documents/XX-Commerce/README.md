# XX Commerce - E-commerce Platform

A comprehensive Django-based e-commerce platform built for educational purposes, featuring a complete shopping experience from product catalog to order management.

## 🚀 Features

### Core E-commerce Functionality
- **Product Catalog**: Browse products by category with search and filtering
- **Shopping Cart**: Add/remove items with real-time updates
- **Checkout Process**: Complete order placement with address management
- **Order Management**: Track order status and history
- **User Authentication**: Registration, login, and profile management
- **Admin Panel**: Full CRUD operations for all models

### Advanced Features
- **Session Management**: Persistent cart for both authenticated and anonymous users
- **Foreign Key Constraints**: Proper database relationships and data integrity
- **Database Indexing**: Optimized queries for better performance
- **Responsive Design**: Mobile-friendly Bootstrap 5 UI
- **Wishlist**: Save favorite products for later
- **Coupon System**: Discount codes and promotional offers
- **Inventory Management**: Stock tracking and backorder support

### Technical Features
- **Django 4.2.7**: Modern web framework
- **MySQL Support**: Production-ready database (SQLite for development)
- **REST API**: JWT authentication for API endpoints
- **Real-time Updates**: WebSocket support with Django Channels
- **Image Management**: Product image galleries with primary image selection
- **SEO Optimized**: Meta tags and clean URLs

## 📋 Requirements

- Python 3.8+
- Django 4.2.7
- MySQL 5.7+ (or SQLite for development)
- Redis (for Channels/WebSocket support)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd XX-Commerce
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### For Development (SQLite)
The project is configured to use SQLite by default for development.

#### For Production (MySQL)
1. Create MySQL database:
```sql
CREATE DATABASE xxcommerce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Update settings.py to use MySQL:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "xxcommerce",
        "USER": "your_username",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
        },
    }
}
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Sample Data
```bash
python manage.py populate_data
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the application.

## 🗄️ Database Schema

### Core Models

#### User Management
- **User**: Django's built-in user model
- **Address**: Customer shipping and billing addresses

#### Product Management
- **Category**: Product categories with hierarchical support
- **Product**: Main product model with inventory tracking
- **ProductImage**: Product images with ordering and primary selection

#### Shopping Experience
- **Cart**: Shopping cart for users and sessions
- **CartItem**: Individual items in shopping cart
- **Wishlist**: User's saved products

#### Order Management
- **Order**: Customer orders with status tracking
- **OrderItem**: Individual items in orders (price snapshots)

#### Promotions
- **Coupon**: Discount codes and promotional offers

### Key Relationships
- Product → Category (Many-to-One)
- OrderItem → Order (Many-to-One)
- OrderItem → Product (Many-to-One)
- CartItem → Cart (Many-to-One)
- CartItem → Product (Many-to-One)
- Address → User (Many-to-One)
- Order → User (Many-to-One)
- Order → Address (Many-to-One for shipping and billing)

### Database Indexes
- Product: name, slug, category, is_active, is_featured, price, sku
- Order: user+created_at, order_number, status, payment_status, created_at
- Category: name, slug, is_active
- Cart: user, session_key, is_active
- Address: user+address_type, user+is_default

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/refresh/` - Refresh JWT token

### Products
- `GET /api/products/` - List products with pagination
- `GET /api/products/{id}/` - Product detail
- `GET /api/categories/` - List categories

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/add/` - Add item to cart
- `PUT /api/cart/update/` - Update cart item
- `DELETE /api/cart/remove/` - Remove item from cart

### Orders
- `GET /api/orders/` - User's order history
- `POST /api/orders/create/` - Create new order
- `GET /api/orders/{id}/` - Order detail

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Database Configuration
DB_NAME=xxcommerce
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Security
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Static Files
```bash
python manage.py collectstatic
```

### Media Files
Media files are served from the `media/` directory during development.

## 🚀 Deployment

### Production Settings
1. Set `DEBUG = False`
2. Configure proper `ALLOWED_HOSTS`
3. Use MySQL database
4. Set up Redis for Channels
5. Configure static file serving with Nginx
6. Use Gunicorn as WSGI server

### Docker Deployment
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "xxcommerce.wsgi:application"]
```

## 📊 Performance Optimizations

### Database Optimizations
- Strategic indexing on frequently queried fields
- Select_related and prefetch_related for foreign keys
- Database query optimization

### Caching
- Redis for session storage
- Template fragment caching
- Database query caching

### Frontend Optimizations
- Image lazy loading
- CSS/JS minification
- CDN for static assets

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Test Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📝 Admin Panel

Access the admin panel at `/admin/` with the superuser account.

### Admin Features
- Product management with image uploads
- Order status updates
- User management
- Category management
- Coupon management
- Inventory tracking

## 🔒 Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password hashing
- JWT token authentication
- Input validation and sanitization

## 📱 Mobile Responsiveness

The application is fully responsive and optimized for:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is created for educational purposes. Please ensure you have the right to use any third-party assets.

## 👥 Team

- **Lead/Architect**: Praja Rosan - Project scope, deployment, order logic, code review
- **Backend A**: Catalog/products implementation
- **Backend B**: Cart/checkout functionality
- **Frontend C**: Templates, UI, responsive design
- **QA/Docs D**: Testing, documentation, teacher-facing demo

## 📞 Support

For questions or support, please contact the development team or create an issue in the repository.

## 🎓 Educational Value

This project demonstrates:
- Django web framework best practices
- Database design with foreign key constraints
- Session management and user authentication
- E-commerce business logic implementation
- REST API development
- Frontend-backend integration
- Database optimization techniques
- Security considerations in web applications

---

**XX Commerce** - A comprehensive e-commerce solution built with Django and modern web technologies.
