# 🛒 Electronics E-Commerce Platform

A modern, full-stack electronics e-commerce platform built with React, FastAPI, and MySQL, featuring advanced product management, search capabilities, and a comprehensive admin dashboard.

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Database Structure](#-database-structure)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [API Overview](#-api-overview)
- [Product System](#-product-system)
- [UI/UX System](#-uiux-system)
- [Error Pages](#-error-pages)
- [Future Improvements](#-future-improvements)
- [Authors](#-authors)
- [License](#-license)

## 🎯 Project Overview

This is a comprehensive electronics e-commerce platform designed to compete with major electronics retailers. The platform specializes in high-quality electronics products including smartphones, laptops, PC components, audio devices, smart devices, and accessories.

### Key Capabilities

- **Admin Dashboard**: Complete product and inventory management system
- **Product Management**: CRUD operations with variants and specifications
- **Interactive Product UI**: Detailed product pages with specifications tables and image hotspots
- **Address Management**: Multi-address support for users
- **Advanced Search**: Autocomplete search with category filtering
- **Responsive Design**: Modern electronics-store UI optimized for all devices

### Technology Stack

- **Frontend**: React 18 + Vite + TypeScript + Redux Toolkit + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy ORM + JWT Authentication
- **Database**: MySQL (primary) / PostgreSQL (compatible)
- **Styling**: Responsive design with modern electronics-store aesthetics

## ✨ Features

### Frontend Features

- **Responsive Electronics-Store UI**: Modern, clean design optimized for electronics shopping
- **Mega Menu Category Dropdown**: Hierarchical category navigation
- **Search Autocomplete Dropdown**: Real-time product search suggestions
- **Product Detail Page**: Comprehensive product information with specifications
- **Product Specifications Table**: Organized technical specifications display
- **Product Variants Selector**: Dynamic variant selection (color, storage, etc.)
- **Related Products**: Intelligent product recommendations
- **Interactive Image Hotspots**: Clickable product image features
- **Breadcrumb Navigation**: Clear navigation hierarchy
- **Dark/Light Mode**: User preference-based theme switching
- **Multi-Language Support**: English and Vietnamese localization
- **Profile Page**: User account management with avatar upload
- **Address Management**: Multiple delivery addresses
- **Cart System**: Persistent shopping cart with quantity management
- **Checkout Flow**: Secure order placement process
- **Order History**: Complete order tracking and history
- **Error Pages**: Dedicated 404, 500, maintenance, and access denied pages

### Backend Features

- **JWT Authentication**: Secure token-based user authentication
- **Role-Based Admin System**: Granular access control for administrators
- **CRUD Product Management**: Complete product lifecycle management
- **Category Hierarchy**: Nested category structure for organization
- **Variant Management**: Product variant handling (size, color, etc.)
- **Product Specifications Management**: Dynamic specification templates
- **Address Management**: User address CRUD operations
- **Order System**: Complete order processing and management
- **Review System**: User product reviews and ratings
- **Upload Image API**: Secure image upload functionality
- **Dynamic Schema Synchronization**: Automatic database schema updates

### Admin Features

- **Add/Edit/Delete Products**: Full product management interface
- **Manage Variants**: Product variant configuration
- **Manage Specifications**: Dynamic specification editing
- **Add Dynamic Specification Rows**: Flexible specification templates
- **Manage Categories**: Category hierarchy management
- **Manage Related Products**: Product relationship configuration
- **Manage Hotspot Features**: Interactive image hotspot setup
- **Manage Inventory**: Stock level monitoring and updates

## 🗄️ Database Structure

The platform uses a relational database with the following core tables:

### Core Tables

- **`users`**: User accounts with authentication and profile information
  - UUID primary keys
  - Email/password authentication
  - Role-based access (user/admin)
  - Avatar URL support
  - Relationships: carts, orders, reviews, addresses

- **`addresses`**: User delivery addresses
  - Multiple addresses per user
  - Default address flag
  - Complete address fields (street, city, country)
  - Foreign key to users with cascade delete

- **`categories`**: Product category hierarchy
  - Unique category names
  - Description field
  - One-to-many relationship with products

- **`products`**: Main product catalog
  - Comprehensive product information
  - Brand, SKU, product type classification
  - Rating and review aggregation
  - Stock management
  - Featured product flag
  - Relationships: category, specifications, cart_items, order_items, reviews

- **`product_specifications`**: Technical specifications
  - Grouped specifications (Display, Performance, etc.)
  - Key-value specification pairs
  - Display order for organization
  - Foreign key to products with cascade delete

- **`spec_templates`**: Specification templates for product types
  - Predefined specs for phones, laptops, audio devices
  - Product type classification
  - Default ordering

- **`reviews`**: User product reviews
  - Rating (1-5 stars) and comments
  - Foreign keys to users and products

- **`carts`**: Shopping cart sessions
  - User-specific carts
  - One-to-many relationship with cart items
  - Foreign key to users with cascade delete

- **`cart_items`**: Individual cart line items
  - Product quantity tracking
  - Foreign keys to carts and products

- **`orders`**: Customer orders
  - Order status tracking
  - Total amount calculation
  - Shipping address integration
  - Payment method recording
  - Relationships: user, address, order_items

- **`order_items`**: Order line items
  - Historical product pricing
  - Quantity and price at time of order
  - Foreign keys to orders and products

### Key Relationships

- **Foreign Keys**: All relationships use UUID foreign keys
- **Cascade Deletes**: Maintains referential integrity
- **Indexing**: Email, product_id, and other frequently queried fields are indexed
- **UUID Primary Keys**: Ensures global uniqueness and security

## 📁 Project Structure

```
├── Frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── Navbar.jsx       # Main navigation with mega menu
│   │   │   ├── SearchBar.jsx    # Search with autocomplete
│   │   │   ├── ProductCard.jsx  # Product display cards
│   │   │   ├── CategoryMegaMenu.jsx # Category navigation
│   │   │   └── ...
│   │   ├── pages/               # Route components
│   │   │   ├── Home.jsx         # Landing page
│   │   │   ├── ProductDetail.jsx # Product detail view
│   │   │   ├── SearchResults.jsx # Search results page
│   │   │   ├── admin/           # Admin dashboard pages
│   │   │   └── ...
│   │   ├── services/            # API service layer
│   │   │   ├── api.js           # Axios configuration
│   │   │   ├── productService.js # Product API calls
│   │   │   └── ...
│   │   ├── store/               # Redux state management
│   │   │   ├── store.js         # Redux store configuration
│   │   │   ├── authSlice.js     # Authentication state
│   │   │   └── ...
│   │   ├── routes/              # Routing configuration
│   │   │   └── AppRoutes.jsx    # Route definitions
│   │   ├── layouts/             # Layout components
│   │   │   ├── MainLayout.jsx   # Main app layout
│   │   │   └── AdminLayout.jsx  # Admin dashboard layout
│   │   ├── hooks/               # Custom React hooks
│   │   └── utils/               # Utility functions
│   ├── index.html               # HTML entry point
│   ├── vite.config.ts           # Vite configuration
│   └── package.json             # Frontend dependencies
│
├── Backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── controllers.py       # API route handlers
│   │   ├── services.py          # Business logic layer
│   │   ├── repositories.py      # Data access layer
│   │   ├── core/                # Core functionality
│   │   │   ├── database.py      # Database configuration
│   │   │   ├── config.py        # App configuration
│   │   │   └── security.py      # JWT and security utilities
│   │   ├── routes/              # Additional route modules
│   │   ├── static/              # Static file serving
│   │   │   └── images/          # Uploaded product images
│   │   └── middleware/          # Custom middleware
│   ├── migrations/              # Database migrations
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Backend-specific documentation
│
├── package.json                 # Root package.json for scripts
└── tsconfig.json               # TypeScript configuration
```

## 🚀 Installation

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- MySQL 8.0+ or PostgreSQL 13+

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd Frontend
   npm install
   ```

2. **Environment Configuration**
   ```bash
   # Create .env file in Frontend/
   VITE_API_URL=http://localhost:8000
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

### Backend Setup

1. **Create Virtual Environment**
   ```bash
   cd Backend
   python -m venv .venv
   # On Windows:
   .\.venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   - Create a MySQL database named `shoppingweb`
   - Update the `.env` file with your database credentials

4. **Environment Configuration**
   ```bash
   # Create .env file in Backend/
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/shoppingweb
   SECRET_KEY=your-secret-key-here
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Start API Server**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`

### Database Seeding (Optional)

For development, you can seed the database with sample electronics products:

```bash
cd Backend
python -m app.seed_data
```

## 🔧 Environment Variables

### Backend (.env)

```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/shoppingweb

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: CORS Origins (comma-separated)
# ALLOWED_ORIGINS=http://localhost:5173,https://yourdomain.com
```

### Frontend (.env)

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Optional: Additional configuration
# VITE_APP_NAME=Electronics Store
```

## 📡 API Overview

The REST API provides comprehensive endpoints for the e-commerce platform:

- **`/auth`**: User authentication (register, login, profile)
- **`/products`**: Product catalog and management
- **`/categories`**: Category hierarchy and navigation
- **`/orders`**: Order processing and history
- **`/cart`**: Shopping cart operations
- **`/reviews`**: Product reviews and ratings
- **`/upload-image`**: Image upload for products
- **`/addresses`**: User address management
- **`/admin`**: Administrative operations and analytics

### Authentication

All protected endpoints require JWT tokens in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## 🛍️ Product System

### Electronics-Oriented Features

- **Product Hierarchy**: Organized by categories (Smartphones, Laptops, Audio, etc.)
- **Brand Management**: Major electronics brands (Apple, Samsung, Sony, etc.)
- **SKU System**: Unique product identification
- **Variant Support**: Color, storage, and configuration variants
- **Dynamic Specifications**: Electronics-specific spec templates
- **Related Products**: Cross-selling recommendations
- **Interactive Hotspots**: Clickable product features on images

### Specification Templates

Pre-configured templates for different product types:

- **Smartphones**: Display, Camera, Performance, Battery specs
- **Laptops**: Display, CPU, GPU, RAM, Storage specs
- **Audio Devices**: Driver, Noise Cancellation, Bluetooth specs

### Product Management

- **CRUD Operations**: Full product lifecycle management
- **Bulk Operations**: Category and inventory management
- **Image Upload**: Multiple product images with hotspot support
- **SEO Optimization**: Meta descriptions and structured data

## 🎨 UI/UX System

### Design Philosophy

- **Electronics-Store Aesthetics**: Clean, modern design inspired by major retailers
- **Responsive Layout**: Optimized for desktop, tablet, and mobile
- **Performance Focused**: Fast loading with lazy image loading
- **Accessibility**: WCAG compliant with keyboard navigation

### Navigation System

- **Mega Menu**: Hierarchical category dropdown navigation
- **Search Dropdown**: Real-time autocomplete suggestions
- **Breadcrumb Navigation**: Clear page hierarchy indication
- **Profile Dropdown**: Quick access to account features

### Theme System

- **Dark/Light Mode**: User preference persistence
- **Consistent Branding**: Electronics-focused color scheme
- **Typography**: Clean, readable font hierarchy

### Error Handling

- **Graceful Degradation**: Offline functionality with banners
- **User-Friendly Messages**: Clear error communication
- **Recovery Options**: Easy retry mechanisms

## 🚨 Error Pages

The platform includes dedicated error pages for better user experience:

- **404 Page**: Custom "Page Not Found" with navigation options
- **500 Page**: Server error page with support contact information
- **Maintenance Page**: Scheduled maintenance notifications
- **403 Page**: Access denied page for unauthorized content

## 🔮 Future Improvements

### Planned Features

- **AI Recommendations**: Machine learning-powered product suggestions
- **Payment Gateway Integration**: Stripe/PayPal payment processing
- **Real-time Notifications**: WebSocket-based order updates
- **Wishlist Sync**: Cross-device wishlist management
- **Elasticsearch**: Advanced search with filters and facets
- **Product Comparison**: Side-by-side product comparison tool
- **Analytics Dashboard**: Advanced admin analytics and reporting

### Technical Enhancements

- **Microservices Architecture**: Service decomposition for scalability
- **Redis Caching**: Performance optimization for frequently accessed data
- **CDN Integration**: Global content delivery for images and assets
- **API Rate Limiting**: Protection against abuse and DoS attacks
- **Automated Testing**: Comprehensive test coverage with CI/CD
- **Container Orchestration**: Kubernetes deployment support

## 👥 Authors

**Development Team**
- Lead Developer: [Your Name]
- Frontend Team: React/TypeScript specialists
- Backend Team: Python/FastAPI developers
- UI/UX Team: Design and user experience experts

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ for the modern electronics shopping experience