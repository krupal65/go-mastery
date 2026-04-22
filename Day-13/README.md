# 🐹 Go Language — Phase 5 
> Complete guide for building a **Production-Ready E-commerce API** in Go
> - **Topic 1: Project Setup**
> - **Topic 2: Choose Project & Define DB Schema + API Endpoints**
> - **Topic 3: Building Features — Auth, CRUD, Filters, File Uploads, Payments (Stripe)**
> - **Topic 4: Optimization & Deployment**

---

## 📚 Table of Contents

- [Topic 1: Project Setup](#topic-1-project-setup)
- [Topic 2: DB Schema & API Endpoints](#topic-2-db-schema--api-endpoints)
- [Topic 3: Building Features](#topic-3-building-features)
  - [Auth — Register & Login](#auth--register--login)
  - [CRUD — Products, Orders, Users](#crud--products-orders-users)
  - [Filters — Search, Pagination, Sort](#filters--search-pagination-sort)
  - [File Uploads — Product Images](#file-uploads--product-images)
  - [Payments — Stripe Integration](#payments--stripe-integration)
- [Topic 4: Optimization & Deployment](#topic-4-optimization--deployment)
- [Interview Questions](#interview-questions)
- [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Topic 1: Project Setup

### Project: E-commerce API

A full-featured REST API for an e-commerce platform with:
- User authentication (JWT)
- Product catalog with categories
- Shopping cart and orders
- File uploads for product images
- Stripe payment processing
- Admin dashboard endpoints
- Redis caching + rate limiting
- Dockerized deployment on AWS EC2

### Folder Structure

```
ecommerce-api/
├── cmd/
│   └── main.go                  ← entry point
├── config/
│   └── config.go                ← env config loader
├── database/
│   └── connect.go               ← DB + Redis connection
├── models/
│   ├── user.go
│   ├── product.go
│   ├── category.go
│   ├── cart.go
│   ├── order.go
│   └── payment.go
├── handlers/
│   ├── auth_handler.go
│   ├── user_handler.go
│   ├── product_handler.go
│   ├── category_handler.go
│   ├── cart_handler.go
│   ├── order_handler.go
│   └── payment_handler.go
├── services/
│   ├── auth_service.go
│   ├── user_service.go
│   ├── product_service.go
│   ├── order_service.go
│   └── payment_service.go
├── middleware/
│   ├── jwt_middleware.go
│   ├── role_middleware.go
│   ├── rate_limit.go
│   └── error_handler.go
├── helpers/
│   ├── response.go              ← standard response helpers
│   ├── file.go                  ← file validation/save
│   └── pagination.go
├── routes/
│   └── routes.go                ← all route definitions
├── uploads/
│   └── products/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── go.mod
└── go.sum
```

### Initialize Project

```bash
# Create project
mkdir ecommerce-api && cd ecommerce-api
go mod init github.com/yourusername/ecommerce-api

# Install all dependencies at once
go get github.com/labstack/echo/v4
go get github.com/labstack/echo/v4/middleware
go get gorm.io/gorm
go get gorm.io/driver/postgres
go get github.com/golang-jwt/jwt/v5
go get golang.org/x/crypto/bcrypt
go get github.com/go-playground/validator/v10
go get github.com/joho/godotenv
go get github.com/redis/go-redis/v9
go get github.com/robfig/cron/v3
go get github.com/stripe/stripe-go/v76
go get gopkg.in/gomail.v2
go get github.com/stretchr/testify
```

### .env.example

```bash
# Server
APP_ENV=development
SERVER_PORT=8080

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=
DB_NAME=ecommerce
DB_SSLMODE=disable

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT
JWT_SECRET=
JWT_EXPIRE_HOURS=24

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
FROM_NAME=EcommerceApp
FROM_EMAIL=

# App
APP_URL=http://localhost:8080
FRONTEND_URL=http://localhost:3000
```

### config/config.go

```go
package config

import (
    "fmt"
    "os"
    "strconv"
)

type Config struct {
    AppEnv      string
    ServerPort  string
    AppURL      string
    FrontendURL string
    DB          DBConfig
    Redis       RedisConfig
    JWT         JWTConfig
    Stripe      StripeConfig
    Email       EmailConfig
}

type DBConfig struct {
    Host, Port, User, Password, Name, SSLMode string
}

type RedisConfig struct {
    Host, Port, Password string
}

type JWTConfig struct {
    Secret      string
    ExpireHours int
}

type StripeConfig struct {
    SecretKey     string
    WebhookSecret string
}

type EmailConfig struct {
    SMTPHost, SMTPUser, SMTPPassword string
    SMTPPort                         int
    FromName, FromEmail              string
}

func (d DBConfig) DSN() string {
    return fmt.Sprintf(
        "postgresql://%s:%s@%s:%s/%s?sslmode=%s",
        d.User, d.Password, d.Host, d.Port, d.Name, d.SSLMode,
    )
}

func Load() *Config {
    return &Config{
        AppEnv:      getEnv("APP_ENV", "development"),
        ServerPort:  getEnv("SERVER_PORT", "8080"),
        AppURL:      getEnv("APP_URL", "http://localhost:8080"),
        FrontendURL: getEnv("FRONTEND_URL", "http://localhost:3000"),
        DB: DBConfig{
            Host:     getEnv("DB_HOST", "localhost"),
            Port:     getEnv("DB_PORT", "5432"),
            User:     getEnv("DB_USER", "postgres"),
            Password: mustGetEnv("DB_PASSWORD"),
            Name:     getEnv("DB_NAME", "ecommerce"),
            SSLMode:  getEnv("DB_SSLMODE", "disable"),
        },
        Redis: RedisConfig{
            Host:     getEnv("REDIS_HOST", "localhost"),
            Port:     getEnv("REDIS_PORT", "6379"),
            Password: getEnv("REDIS_PASSWORD", ""),
        },
        JWT: JWTConfig{
            Secret:      mustGetEnv("JWT_SECRET"),
            ExpireHours: getEnvInt("JWT_EXPIRE_HOURS", 24),
        },
        Stripe: StripeConfig{
            SecretKey:     mustGetEnv("STRIPE_SECRET_KEY"),
            WebhookSecret: getEnv("STRIPE_WEBHOOK_SECRET", ""),
        },
    }
}

func getEnv(k, d string) string {
    if v := os.Getenv(k); v != "" { return v }
    return d
}
func mustGetEnv(k string) string {
    v := os.Getenv(k)
    if v == "" { panic("required env var not set: " + k) }
    return v
}
func getEnvInt(k string, d int) int {
    if v := os.Getenv(k); v != "" {
        if i, err := strconv.Atoi(v); err == nil { return i }
    }
    return d
}
```

---

## Topic 2: DB Schema & API Endpoints

### Database Schema

```sql
-- Users
CREATE TABLE users (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL,
    role       VARCHAR(20)  NOT NULL DEFAULT 'customer',
    is_active  BOOLEAN      NOT NULL DEFAULT true,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Categories
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    image_url   VARCHAR(500),
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    slug         VARCHAR(255) UNIQUE NOT NULL,
    description  TEXT,
    price        DECIMAL(10,2) NOT NULL,
    sale_price   DECIMAL(10,2),
    stock        INTEGER NOT NULL DEFAULT 0,
    category_id  INTEGER REFERENCES categories(id),
    image_url    VARCHAR(500),
    images       JSONB,              -- multiple images
    is_active    BOOLEAN DEFAULT true,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at   TIMESTAMP
);

-- Cart Items
CREATE TABLE cart_items (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity   INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)      -- one entry per product per user
);

-- Orders
CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    status          VARCHAR(30) NOT NULL DEFAULT 'pending',
    total_amount    DECIMAL(10,2) NOT NULL,
    shipping_address JSONB NOT NULL,
    payment_status  VARCHAR(20) DEFAULT 'pending',
    payment_intent_id VARCHAR(255),   -- Stripe payment intent ID
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Items
CREATE TABLE order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity   INTEGER NOT NULL,
    price      DECIMAL(10,2) NOT NULL,  -- price at time of purchase
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments
CREATE TABLE payments (
    id                SERIAL PRIMARY KEY,
    order_id          INTEGER REFERENCES orders(id),
    amount            DECIMAL(10,2) NOT NULL,
    currency          VARCHAR(10) NOT NULL DEFAULT 'usd',
    status            VARCHAR(30) NOT NULL,
    payment_intent_id VARCHAR(255) UNIQUE,
    stripe_charge_id  VARCHAR(255),
    failure_reason    TEXT,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_products_category   ON products(category_id);
CREATE INDEX idx_products_slug       ON products(slug);
CREATE INDEX idx_cart_items_user     ON cart_items(user_id);
CREATE INDEX idx_orders_user         ON orders(user_id);
CREATE INDEX idx_orders_status       ON orders(status);
```

### GORM Models

```go
// models/user.go
type User struct {
    gorm.Model
    Name      string  `gorm:"size:100;not null"         json:"name"`
    Email     string  `gorm:"uniqueIndex;not null"      json:"email"`
    Password  string  `gorm:"not null"                  json:"-"`
    Role      string  `gorm:"size:20;default:'customer'" json:"role"`
    IsActive  bool    `gorm:"default:true"              json:"is_active"`
    AvatarURL string  `gorm:"size:500"                  json:"avatar_url,omitempty"`
}

// models/product.go
type Product struct {
    gorm.Model
    Name        string          `gorm:"size:255;not null"  json:"name"`
    Slug        string          `gorm:"uniqueIndex;not null" json:"slug"`
    Description string          `gorm:"type:text"          json:"description"`
    Price       float64         `gorm:"not null"           json:"price"`
    SalePrice   *float64        `json:"sale_price,omitempty"`
    Stock       int             `gorm:"default:0"          json:"stock"`
    CategoryID  uint            `json:"category_id"`
    Category    Category        `gorm:"foreignKey:CategoryID" json:"category,omitempty"`
    ImageURL    string          `gorm:"size:500"           json:"image_url"`
    IsActive    bool            `gorm:"default:true"       json:"is_active"`
}

// models/order.go
type Order struct {
    gorm.Model
    UserID          uint           `json:"user_id"`
    User            User           `gorm:"foreignKey:UserID" json:"user,omitempty"`
    Status          string         `gorm:"size:30;default:'pending'" json:"status"`
    TotalAmount     float64        `json:"total_amount"`
    ShippingAddress datatypes.JSON `json:"shipping_address"`
    PaymentStatus   string         `gorm:"default:'pending'"  json:"payment_status"`
    PaymentIntentID string         `json:"payment_intent_id,omitempty"`
    Items           []OrderItem    `gorm:"foreignKey:OrderID" json:"items,omitempty"`
}

type OrderItem struct {
    gorm.Model
    OrderID   uint    `json:"order_id"`
    ProductID uint    `json:"product_id"`
    Product   Product `gorm:"foreignKey:ProductID" json:"product,omitempty"`
    Quantity  int     `json:"quantity"`
    Price     float64 `json:"price"`
}
```

### API Endpoints — Complete List

```
════════════════════════════════════════════════════════
  AUTH ENDPOINTS (public)
════════════════════════════════════════════════════════
POST   /api/v1/auth/register        Register new user
POST   /api/v1/auth/login           Login → returns JWT
POST   /api/v1/auth/refresh         Refresh access token
POST   /api/v1/auth/forgot-password Send reset email
POST   /api/v1/auth/reset-password  Reset password

════════════════════════════════════════════════════════
  USER ENDPOINTS (authenticated)
════════════════════════════════════════════════════════
GET    /api/v1/users/profile        Get own profile
PUT    /api/v1/users/profile        Update own profile
POST   /api/v1/users/avatar         Upload avatar image
PUT    /api/v1/users/password       Change password

════════════════════════════════════════════════════════
  PRODUCT ENDPOINTS (public GET, admin POST/PUT/DELETE)
════════════════════════════════════════════════════════
GET    /api/v1/products             List products (paginated, filtered, sorted)
GET    /api/v1/products/:id         Get product by ID
GET    /api/v1/products/slug/:slug  Get product by slug
POST   /api/v1/products             [admin] Create product
PUT    /api/v1/products/:id         [admin] Update product
DELETE /api/v1/products/:id         [admin] Delete product
POST   /api/v1/products/:id/images  [admin] Upload product images

════════════════════════════════════════════════════════
  CATEGORY ENDPOINTS
════════════════════════════════════════════════════════
GET    /api/v1/categories           List all categories
GET    /api/v1/categories/:id       Get category + products
POST   /api/v1/categories           [admin] Create category
PUT    /api/v1/categories/:id       [admin] Update category
DELETE /api/v1/categories/:id       [admin] Delete category

════════════════════════════════════════════════════════
  CART ENDPOINTS (authenticated)
════════════════════════════════════════════════════════
GET    /api/v1/cart                 Get user's cart
POST   /api/v1/cart                 Add item to cart
PUT    /api/v1/cart/:product_id     Update item quantity
DELETE /api/v1/cart/:product_id     Remove item from cart
DELETE /api/v1/cart                 Clear entire cart

════════════════════════════════════════════════════════
  ORDER ENDPOINTS (authenticated)
════════════════════════════════════════════════════════
GET    /api/v1/orders               Get user's orders
GET    /api/v1/orders/:id           Get order details
POST   /api/v1/orders               Create order from cart
PUT    /api/v1/orders/:id/cancel    Cancel order

════════════════════════════════════════════════════════
  PAYMENT ENDPOINTS
════════════════════════════════════════════════════════
POST   /api/v1/payments/intent      Create Stripe payment intent
POST   /api/v1/payments/confirm     Confirm payment
POST   /api/v1/payments/webhook     Stripe webhook (public)
GET    /api/v1/payments/history     User's payment history

════════════════════════════════════════════════════════
  ADMIN ENDPOINTS
════════════════════════════════════════════════════════
GET    /api/v1/admin/users          List all users
PUT    /api/v1/admin/users/:id/role Assign role
GET    /api/v1/admin/orders         All orders with filters
PUT    /api/v1/admin/orders/:id/status Update order status
GET    /api/v1/admin/stats          Dashboard stats
GET    /api/v1/admin/revenue        Revenue report
```

---

## Topic 3: Building Features

### Auth — Register & Login

```go
// handlers/auth_handler.go
type AuthHandler struct {
    db           *gorm.DB
    rdb          *redis.Client
    cfg          *config.Config
    emailSvc     email.Service
}

func (h *AuthHandler) Register(c echo.Context) error {
    var req struct {
        Name     string `json:"name"     validate:"required,min=2,max=100"`
        Email    string `json:"email"    validate:"required,email"`
        Password string `json:"password" validate:"required,min=8"`
    }

    if err := c.Bind(&req); err != nil {
        return echo.NewHTTPError(400, "invalid request body")
    }
    if err := c.Validate(&req); err != nil {
        return err
    }

    // Check duplicate email
    var count int64
    h.db.Model(&models.User{}).Where("email = ?", req.Email).Count(&count)
    if count > 0 {
        return echo.NewHTTPError(409, "email already registered")
    }

    // Hash password
    hash, err := bcrypt.GenerateFromPassword([]byte(req.Password), 12)
    if err != nil {
        return echo.NewHTTPError(500, "could not process password")
    }

    // Create user
    user := models.User{Name: req.Name, Email: req.Email, Password: string(hash)}
    if err := h.db.Create(&user).Error; err != nil {
        return echo.NewHTTPError(500, "could not create user")
    }

    // Generate token
    token, _ := generateToken(user.ID, user.Email, user.Role, h.cfg.JWT.Secret)

    // Send welcome email (async)
    go h.emailSvc.SendWelcome(user.Email, user.Name)

    return c.JSON(201, map[string]interface{}{
        "user":  user,
        "token": token,
    })
}

func (h *AuthHandler) Login(c echo.Context) error {
    var req struct {
        Email    string `json:"email"    validate:"required,email"`
        Password string `json:"password" validate:"required"`
    }
    c.Bind(&req)
    c.Validate(&req)

    var user models.User
    if err := h.db.Where("email = ?", req.Email).First(&user).Error; err != nil {
        return echo.NewHTTPError(401, "invalid email or password")
    }

    if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password)); err != nil {
        return echo.NewHTTPError(401, "invalid email or password")
    }

    if !user.IsActive {
        return echo.NewHTTPError(403, "account is deactivated")
    }

    token, _ := generateToken(user.ID, user.Email, user.Role, h.cfg.JWT.Secret)
    return c.JSON(200, map[string]interface{}{"user": user, "token": token})
}
```

### CRUD — Products with Filters

```go
// handlers/product_handler.go

type ProductQuery struct {
    Page       int     `query:"page"`
    Limit      int     `query:"limit"`
    Search     string  `query:"search"`
    CategoryID uint    `query:"category_id"`
    MinPrice   float64 `query:"min_price"`
    MaxPrice   float64 `query:"max_price"`
    InStock    *bool   `query:"in_stock"`
    SortBy     string  `query:"sort_by"`
    SortOrder  string  `query:"sort_order"`
}

func (h *ProductHandler) GetProducts(c echo.Context) error {
    var q ProductQuery
    c.Bind(&q)

    // Defaults
    if q.Page  <= 0   { q.Page  = 1  }
    if q.Limit <= 0   { q.Limit = 12 }
    if q.Limit > 100  { q.Limit = 100 }
    if q.SortBy == "" { q.SortBy = "created_at" }
    if q.SortOrder == "" { q.SortOrder = "desc" }

    // Build query
    query := h.db.Model(&models.Product{}).
        Where("is_active = ?", true).
        Preload("Category")

    if q.Search != "" {
        query = query.Where("name ILIKE ? OR description ILIKE ?",
            "%"+q.Search+"%", "%"+q.Search+"%")
    }
    if q.CategoryID > 0 {
        query = query.Where("category_id = ?", q.CategoryID)
    }
    if q.MinPrice > 0 {
        query = query.Where("price >= ?", q.MinPrice)
    }
    if q.MaxPrice > 0 {
        query = query.Where("price <= ?", q.MaxPrice)
    }
    if q.InStock != nil && *q.InStock {
        query = query.Where("stock > 0")
    }

    // Count total
    var total int64
    query.Count(&total)

    // Safe sort
    allowed := map[string]bool{"name": true, "price": true, "created_at": true, "stock": true}
    sortBy := q.SortBy
    if !allowed[sortBy] { sortBy = "created_at" }
    if q.SortOrder != "asc" { q.SortOrder = "desc" }

    var products []models.Product
    query.Order(fmt.Sprintf("%s %s", sortBy, q.SortOrder)).
        Offset((q.Page - 1) * q.Limit).
        Limit(q.Limit).
        Find(&products)

    totalPages := int(math.Ceil(float64(total) / float64(q.Limit)))
    return c.JSON(200, map[string]interface{}{
        "data":        products,
        "page":        q.Page,
        "limit":       q.Limit,
        "total":       total,
        "total_pages": totalPages,
        "has_next":    q.Page < totalPages,
    })
}

func (h *ProductHandler) CreateProduct(c echo.Context) error {
    var req struct {
        Name        string  `json:"name"        validate:"required,min=2,max=255"`
        Description string  `json:"description"`
        Price       float64 `json:"price"       validate:"required,gt=0"`
        Stock       int     `json:"stock"       validate:"min=0"`
        CategoryID  uint    `json:"category_id" validate:"required"`
    }
    c.Bind(&req)
    c.Validate(&req)

    // Generate slug
    slug := generateSlug(req.Name)

    product := models.Product{
        Name:        req.Name,
        Slug:        slug,
        Description: req.Description,
        Price:       req.Price,
        Stock:       req.Stock,
        CategoryID:  req.CategoryID,
    }
    h.db.Create(&product)

    return c.JSON(201, product)
}
```

### Cart Operations

```go
// handlers/cart_handler.go

func (h *CartHandler) AddToCart(c echo.Context) error {
    userID := c.Get("user_id").(uint)

    var req struct {
        ProductID uint `json:"product_id" validate:"required"`
        Quantity  int  `json:"quantity"   validate:"required,min=1,max=99"`
    }
    c.Bind(&req)
    c.Validate(&req)

    // Check product exists and has stock
    var product models.Product
    if err := h.db.First(&product, req.ProductID).Error; err != nil {
        return echo.NewHTTPError(404, "product not found")
    }
    if product.Stock < req.Quantity {
        return echo.NewHTTPError(400, fmt.Sprintf("only %d items in stock", product.Stock))
    }

    // Upsert cart item — add quantity if already in cart
    var item models.CartItem
    result := h.db.Where("user_id = ? AND product_id = ?", userID, req.ProductID).First(&item)

    if result.Error == gorm.ErrRecordNotFound {
        // New item
        item = models.CartItem{UserID: userID, ProductID: req.ProductID, Quantity: req.Quantity}
        h.db.Create(&item)
    } else {
        // Update quantity
        h.db.Model(&item).Update("quantity", item.Quantity+req.Quantity)
    }

    return c.JSON(200, map[string]string{"message": "added to cart"})
}

func (h *CartHandler) GetCart(c echo.Context) error {
    userID := c.Get("user_id").(uint)

    var items []models.CartItem
    h.db.Where("user_id = ?", userID).
        Preload("Product").
        Preload("Product.Category").
        Find(&items)

    // Calculate total
    total := 0.0
    for _, item := range items {
        price := item.Product.Price
        if item.Product.SalePrice != nil {
            price = *item.Product.SalePrice
        }
        total += price * float64(item.Quantity)
    }

    return c.JSON(200, map[string]interface{}{
        "items": items,
        "total": total,
        "count": len(items),
    })
}
```

### File Uploads — Product Images

```go
// handlers/upload_handler.go

func (h *ProductHandler) UploadImage(c echo.Context) error {
    // Only admin
    productID, _ := strconv.Atoi(c.Param("id"))

    file, err := c.FormFile("image")
    if err != nil {
        return echo.NewHTTPError(400, "image file is required")
    }

    // Validate
    allowed := map[string]bool{"image/jpeg": true, "image/png": true, "image/webp": true}
    if !allowed[file.Header.Get("Content-Type")] {
        return echo.NewHTTPError(400, "only JPEG, PNG, WebP allowed")
    }
    if file.Size > 5*1024*1024 {
        return echo.NewHTTPError(400, "image must not exceed 5MB")
    }

    // Save file
    ext      := filepath.Ext(file.Filename)
    filename := fmt.Sprintf("%d_%d%s", productID, time.Now().UnixNano(), ext)
    path     := filepath.Join("uploads", "products", filename)
    os.MkdirAll(filepath.Dir(path), 0755)

    src, _ := file.Open()
    dst, _ := os.Create(path)
    defer src.Close()
    defer dst.Close()
    io.Copy(dst, src)

    // Update product image URL
    imageURL := "/uploads/products/" + filename
    h.db.Model(&models.Product{}).Where("id = ?", productID).
        Update("image_url", imageURL)

    return c.JSON(200, map[string]string{
        "image_url": imageURL,
        "message":   "image uploaded successfully",
    })
}
```

### Payments — Stripe Integration

```bash
go get github.com/stripe/stripe-go/v76
```

```go
// handlers/payment_handler.go
package handlers

import (
    "github.com/stripe/stripe-go/v76"
    "github.com/stripe/stripe-go/v76/paymentintent"
    "github.com/stripe/stripe-go/v76/webhook"
)

type PaymentHandler struct {
    db  *gorm.DB
    cfg *config.Config
}

// Step 1: Create Payment Intent — called when user clicks "Pay"
func (h *PaymentHandler) CreatePaymentIntent(c echo.Context) error {
    userID := c.Get("user_id").(uint)

    var req struct {
        OrderID uint `json:"order_id" validate:"required"`
    }
    c.Bind(&req)

    // Get order
    var order models.Order
    if err := h.db.Where("id = ? AND user_id = ?", req.OrderID, userID).
        First(&order).Error; err != nil {
        return echo.NewHTTPError(404, "order not found")
    }
    if order.PaymentStatus == "paid" {
        return echo.NewHTTPError(400, "order already paid")
    }

    // Initialize Stripe
    stripe.Key = h.cfg.Stripe.SecretKey

    // Create Payment Intent
    // Amount in smallest currency unit (paise for INR, cents for USD)
    params := &stripe.PaymentIntentParams{
        Amount:   stripe.Int64(int64(order.TotalAmount * 100)),
        Currency: stripe.String("usd"),
        Metadata: map[string]string{
            "order_id": fmt.Sprintf("%d", order.ID),
            "user_id":  fmt.Sprintf("%d", userID),
        },
    }
    pi, err := paymentintent.New(params)
    if err != nil {
        return echo.NewHTTPError(500, "payment initiation failed")
    }

    // Save payment intent ID to order
    h.db.Model(&order).Update("payment_intent_id", pi.ID)

    // Return client_secret to frontend for Stripe.js
    return c.JSON(200, map[string]string{
        "client_secret":     pi.ClientSecret,
        "payment_intent_id": pi.ID,
    })
}

// Step 2: Stripe Webhook — called by Stripe when payment completes
// This is how Stripe tells your server the payment succeeded/failed
func (h *PaymentHandler) HandleWebhook(c echo.Context) error {
    payload, err := io.ReadAll(c.Request().Body)
    if err != nil {
        return echo.NewHTTPError(400, "could not read body")
    }

    // Verify webhook signature — IMPORTANT for security!
    sig := c.Request().Header.Get("Stripe-Signature")
    event, err := webhook.ConstructEvent(payload, sig, h.cfg.Stripe.WebhookSecret)
    if err != nil {
        return echo.NewHTTPError(400, "invalid webhook signature")
    }

    // Handle different event types
    switch event.Type {

    case "payment_intent.succeeded":
        var pi stripe.PaymentIntent
        json.Unmarshal(event.Data.Raw, &pi)

        // Update order status
        h.db.Model(&models.Order{}).
            Where("payment_intent_id = ?", pi.ID).
            Updates(map[string]interface{}{
                "payment_status": "paid",
                "status":         "confirmed",
            })

        // Record payment
        orderID, _ := strconv.Atoi(pi.Metadata["order_id"])
        h.db.Create(&models.Payment{
            OrderID:         uint(orderID),
            Amount:          float64(pi.Amount) / 100,
            Currency:        string(pi.Currency),
            Status:          "succeeded",
            PaymentIntentID: pi.ID,
        })
        log.Printf("Payment succeeded for order %d", orderID)

    case "payment_intent.payment_failed":
        var pi stripe.PaymentIntent
        json.Unmarshal(event.Data.Raw, &pi)

        h.db.Model(&models.Order{}).
            Where("payment_intent_id = ?", pi.ID).
            Update("payment_status", "failed")

        log.Printf("Payment failed: %s", pi.LastPaymentError.Message)
    }

    return c.JSON(200, map[string]string{"received": "true"})
}
```

---

## Topic 4: Optimization & Deployment

### Optimize Queries

```go
// ── 1. Use indexes for frequently queried columns ─────────────
// In GORM model tags:
Email    string `gorm:"uniqueIndex"`          // unique index
Slug     string `gorm:"uniqueIndex"`
Status   string `gorm:"index"`                // regular index
Category uint   `gorm:"index:idx_cat_active"` // composite index

// Or raw SQL for custom indexes:
// CREATE INDEX idx_products_search ON products USING gin(to_tsvector('english', name || ' ' || description));

// ── 2. Select only needed columns ─────────────────────────────
// Bad — fetches ALL columns including unused ones
db.Find(&products)

// Good — only fetch what you need
db.Select("id", "name", "price", "image_url").Find(&products)

// ── 3. Use Preload instead of N+1 queries ─────────────────────
// Bad — N+1: 1 query for orders + N queries for each user
for _, order := range orders {
    db.First(&order.User, order.UserID)  // N separate queries!
}

// Good — 2 queries total
db.Preload("User").Preload("Items").Find(&orders)

// ── 4. Redis caching for hot data ─────────────────────────────
func (s *ProductService) GetProduct(id uint) (*models.Product, error) {
    key := fmt.Sprintf("product:%d", id)

    // Check cache
    if cached, err := s.rdb.Get(ctx, key).Result(); err == nil {
        var p models.Product
        json.Unmarshal([]byte(cached), &p)
        return &p, nil
    }

    // DB query
    var p models.Product
    s.db.Preload("Category").First(&p, id)

    // Cache for 10 minutes
    data, _ := json.Marshal(p)
    s.rdb.Set(ctx, key, data, 10*time.Minute)
    return &p, nil
}

// ── 5. Pagination — always limit results ──────────────────────
// Never do: db.Find(&products) — could return 1 million rows!
// Always: db.Limit(20).Offset(offset).Find(&products)

// ── 6. Use transactions for multi-step operations ─────────────
func (s *OrderService) CreateOrder(userID uint, address Address) (*models.Order, error) {
    tx := s.db.Begin()
    defer func() {
        if r := recover(); r != nil { tx.Rollback() }
    }()

    // 1. Get cart items
    var cartItems []models.CartItem
    tx.Where("user_id = ?", userID).Preload("Product").Find(&cartItems)
    if len(cartItems) == 0 {
        tx.Rollback()
        return nil, errors.New("cart is empty")
    }

    // 2. Calculate total
    total := 0.0
    for _, item := range cartItems {
        total += item.Product.Price * float64(item.Quantity)
    }

    // 3. Create order
    order := models.Order{UserID: userID, TotalAmount: total, Status: "pending"}
    tx.Create(&order)

    // 4. Create order items + reduce stock
    for _, item := range cartItems {
        tx.Create(&models.OrderItem{
            OrderID: order.ID, ProductID: item.ProductID,
            Quantity: item.Quantity, Price: item.Product.Price,
        })
        // Reduce stock atomically
        tx.Model(&models.Product{}).Where("id = ?", item.ProductID).
            Update("stock", gorm.Expr("stock - ?", item.Quantity))
    }

    // 5. Clear cart
    tx.Where("user_id = ?", userID).Delete(&models.CartItem{})

    tx.Commit()
    return &order, nil
}
```

### Admin Dashboard Stats

```go
// handlers/admin_handler.go
func (h *AdminHandler) GetStats(c echo.Context) error {
    ctx := context.Background()
    cacheKey := "admin:stats"

    // Cache stats for 5 minutes
    if cached, err := h.rdb.Get(ctx, cacheKey).Result(); err == nil {
        var stats map[string]interface{}
        json.Unmarshal([]byte(cached), &stats)
        return c.JSON(200, stats)
    }

    var (
        totalUsers    int64
        totalProducts int64
        totalOrders   int64
        revenue       float64
    )

    h.db.Model(&models.User{}).Count(&totalUsers)
    h.db.Model(&models.Product{}).Where("is_active = ?", true).Count(&totalProducts)
    h.db.Model(&models.Order{}).Where("status != ?", "cancelled").Count(&totalOrders)
    h.db.Model(&models.Order{}).
        Where("payment_status = ?", "paid").
        Select("COALESCE(SUM(total_amount), 0)").
        Scan(&revenue)

    stats := map[string]interface{}{
        "total_users":    totalUsers,
        "total_products": totalProducts,
        "total_orders":   totalOrders,
        "total_revenue":  revenue,
        "generated_at":   time.Now(),
    }

    data, _ := json.Marshal(stats)
    h.rdb.Set(ctx, cacheKey, data, 5*time.Minute)

    return c.JSON(200, stats)
}
```

### cmd/main.go — Complete Entry Point

```go
package main

import (
    "log"
    "github.com/joho/godotenv"
    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
    "github.com/go-playground/validator/v10"

    "ecommerce-api/config"
    "ecommerce-api/database"
    "ecommerce-api/handlers"
    appmw "ecommerce-api/middleware"
    "ecommerce-api/models"
    "ecommerce-api/routes"
)

type CustomValidator struct{ v *validator.Validate }
func (cv *CustomValidator) Validate(i interface{}) error {
    if err := cv.v.Struct(i); err != nil {
        return echo.NewHTTPError(422, err.Error())
    }
    return nil
}

func main() {
    // 1. Load env
    godotenv.Load()
    cfg := config.Load()
    log.Printf("Starting %s in %s mode", "ecommerce-api", cfg.AppEnv)

    // 2. Connect DB
    db, err := database.Connect(cfg.DB.DSN(), 25, 10)
    if err != nil { log.Fatal("DB failed:", err) }

    // 3. Run migrations
    db.AutoMigrate(
        &models.User{}, &models.Category{}, &models.Product{},
        &models.CartItem{}, &models.Order{}, &models.OrderItem{},
        &models.Payment{},
    )

    // 4. Connect Redis
    rdb := database.ConnectRedis(cfg.Redis)

    // 5. Setup Echo
    e := echo.New()
    e.HideBanner = true
    e.Validator = &CustomValidator{v: validator.New()}
    e.HTTPErrorHandler = appmw.GlobalErrorHandler

    // 6. Global middleware
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())
    e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
        AllowOrigins: []string{cfg.FrontendURL},
        AllowMethods: []string{"GET","POST","PUT","DELETE","PATCH"},
        AllowHeaders: []string{"Content-Type","Authorization"},
    }))

    // 7. Static files
    e.Static("/uploads", "uploads")

    // 8. Health check
    e.GET("/health", func(c echo.Context) error {
        return c.JSON(200, map[string]string{"status": "healthy"})
    })

    // 9. Register routes
    routes.Register(e, db, rdb, cfg)

    // 10. Start
    log.Printf("Server starting on :%s", cfg.ServerPort)
    e.Logger.Fatal(e.Start(":"+cfg.ServerPort))
}
```

### routes/routes.go

```go
package routes

func Register(e *echo.Echo, db *gorm.DB, rdb *redis.Client, cfg *config.Config) {
    // Init handlers
    authH    := handlers.NewAuthHandler(db, rdb, cfg)
    userH    := handlers.NewUserHandler(db, rdb)
    productH := handlers.NewProductHandler(db, rdb)
    cartH    := handlers.NewCartHandler(db)
    orderH   := handlers.NewOrderHandler(db)
    payH     := handlers.NewPaymentHandler(db, cfg)
    adminH   := handlers.NewAdminHandler(db, rdb)

    // Middleware
    jwtMW   := middleware.JWTMiddleware(cfg.JWT.Secret)
    adminMW := middleware.RoleMiddleware("admin")

    v1 := e.Group("/api/v1")

    // Public auth routes
    auth := v1.Group("/auth")
    auth.POST("/register",        authH.Register)
    auth.POST("/login",           authH.Login)
    auth.POST("/forgot-password", authH.ForgotPassword)
    auth.POST("/reset-password",  authH.ResetPassword)

    // Public product routes
    prods := v1.Group("/products")
    prods.GET("",          productH.GetProducts)
    prods.GET("/:id",      productH.GetProductByID)
    prods.GET("/slug/:slug", productH.GetProductBySlug)

    // Public categories
    cats := v1.Group("/categories")
    cats.GET("",     productH.GetCategories)
    cats.GET("/:id", productH.GetCategoryProducts)

    // Stripe webhook (public — no auth, verified by signature)
    v1.POST("/payments/webhook", payH.HandleWebhook)

    // Authenticated routes
    protected := v1.Group("", jwtMW)

    protected.GET("/users/profile",      userH.GetProfile)
    protected.PUT("/users/profile",      userH.UpdateProfile)
    protected.POST("/users/avatar",      userH.UploadAvatar)
    protected.PUT("/users/password",     authH.ChangePassword)

    protected.GET("/cart",                 cartH.GetCart)
    protected.POST("/cart",                cartH.AddToCart)
    protected.PUT("/cart/:product_id",     cartH.UpdateQuantity)
    protected.DELETE("/cart/:product_id",  cartH.RemoveFromCart)
    protected.DELETE("/cart",              cartH.ClearCart)

    protected.GET("/orders",           orderH.GetOrders)
    protected.GET("/orders/:id",       orderH.GetOrderByID)
    protected.POST("/orders",          orderH.CreateOrder)
    protected.PUT("/orders/:id/cancel", orderH.CancelOrder)

    protected.POST("/payments/intent",  payH.CreatePaymentIntent)
    protected.GET("/payments/history",  payH.GetPaymentHistory)

    // Admin routes
    admin := v1.Group("/admin", jwtMW, adminMW)
    admin.GET("/users",                adminH.GetAllUsers)
    admin.PUT("/users/:id/role",       adminH.AssignRole)
    admin.GET("/orders",               adminH.GetAllOrders)
    admin.PUT("/orders/:id/status",    adminH.UpdateOrderStatus)
    admin.GET("/stats",                adminH.GetStats)
    admin.POST("/products",            productH.CreateProduct)
    admin.PUT("/products/:id",         productH.UpdateProduct)
    admin.DELETE("/products/:id",      productH.DeleteProduct)
    admin.POST("/products/:id/images", productH.UploadImage)
    admin.POST("/categories",          productH.CreateCategory)
    admin.PUT("/categories/:id",       productH.UpdateCategory)
}
```

### Deploy Live

```bash
# ── 1. Build and push Docker image ────────────────────────────
docker build -t yourusername/ecommerce-api:latest .
docker push yourusername/ecommerce-api:latest

# ── 2. SSH into EC2 ───────────────────────────────────────────
ssh -i mykey.pem ubuntu@YOUR_EC2_IP

# ── 3. Setup on EC2 ───────────────────────────────────────────
git clone https://github.com/yourusername/ecommerce-api.git
cd ecommerce-api
cp .env.example .env
nano .env   # fill all production values

# ── 4. Start all services ─────────────────────────────────────
docker compose up -d
docker compose ps       # verify all running
docker compose logs -f  # watch logs

# ── 5. Setup Nginx ────────────────────────────────────────────
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/ecommerce-api
sudo ln -s /etc/nginx/sites-available/ecommerce-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# ── 6. HTTPS ──────────────────────────────────────────────────
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com

# ── 7. Verify ─────────────────────────────────────────────────
curl https://yourdomain.com/health
# {"status":"healthy"} ✅

# ── 8. Test API ───────────────────────────────────────────────
curl -X POST https://yourdomain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Rahul","email":"rahul@test.com","password":"secret123"}'
```

---

## Interview Questions

**Q: How would you design the database schema for an e-commerce API?**
> Core tables: users, categories, products, cart_items, orders, order_items, payments. Products have a category_id foreign key. cart_items has UNIQUE(user_id, product_id) to prevent duplicates. orders stores payment_intent_id from Stripe. order_items stores price at time of purchase (snapshot) because product price can change later. Use DECIMAL(10,2) for money — never float.

**Q: How does Stripe payment flow work in a Go API?**
> Three steps: (1) Client clicks Pay → API calls `paymentintent.New()` → returns `client_secret` to frontend. (2) Frontend uses Stripe.js with `client_secret` to collect card and confirm payment directly with Stripe. (3) Stripe calls your webhook endpoint → verify signature → update order status. Never store card data yourself.

**Q: Why verify the Stripe webhook signature?**
> Anyone can POST to your webhook URL. Stripe signs every webhook with your `STRIPE_WEBHOOK_SECRET`. Use `webhook.ConstructEvent(payload, sig, secret)` to verify the signature. Reject any request where verification fails — it's not from Stripe. This prevents attackers from faking payment success events.

**Q: How do you prevent race conditions when reducing product stock?**
> Use a transaction with `gorm.Expr("stock - ?", qty)` for atomic update. Also add a check: `WHERE stock >= qty` to prevent negative stock. Better yet, use database-level constraint: `CHECK (stock >= 0)`. For high-traffic scenarios, use Redis DECR for atomic decrement with a DB sync.

**Q: How would you optimize a slow `GET /products` endpoint?**
> (1) Database indexes on commonly filtered columns (category_id, price, is_active). (2) Select only needed columns instead of SELECT *. (3) Use LIMIT/OFFSET — never return all records. (4) Redis cache the response for 5-10 minutes, invalidate on product updates. (5) Use database-level full-text search index for text search instead of ILIKE.

**Q: What is the N+1 query problem and how do you solve it in GORM?**
> N+1 occurs when you load N records and then run 1 extra query for each. Example: loading 20 orders then querying each order's user separately = 21 queries. Solve with `db.Preload("User").Preload("Items").Find(&orders)` — GORM does 2 queries regardless of N.

**Q: How do you handle the cart-to-order transition atomically?**
> Use a database transaction: BEGIN → validate cart items → check stock → create order → create order_items → reduce stock (`stock - qty`) → clear cart → COMMIT. If any step fails, ROLLBACK undoes all changes. This ensures no partial states (order created but stock not reduced, etc.).

---

## Quick Reference Cheatsheet

```bash
# ── PROJECT INIT ───────────────────────────────────────────────
go mod init github.com/user/ecommerce-api
go get github.com/labstack/echo/v4 gorm.io/gorm gorm.io/driver/postgres
go get github.com/golang-jwt/jwt/v5 golang.org/x/crypto/bcrypt
go get github.com/stripe/stripe-go/v76 github.com/redis/go-redis/v9
go get github.com/go-playground/validator/v10 github.com/joho/godotenv
```

```go
// ── ORDER STATUS FLOW ──────────────────────────────────────────
// pending → confirmed (after payment) → processing → shipped → delivered
// pending → cancelled (before payment or by user/admin)

// ── STRIPE FLOW ────────────────────────────────────────────────
stripe.Key = cfg.Stripe.SecretKey
pi, _ := paymentintent.New(&stripe.PaymentIntentParams{
    Amount:   stripe.Int64(int64(amount * 100)),  // cents
    Currency: stripe.String("usd"),
})
// Return pi.ClientSecret to frontend
// Frontend uses Stripe.js to confirm payment
// Stripe calls webhook on success/failure

// Verify webhook
event, err := webhook.ConstructEvent(payload, sig, webhookSecret)
switch event.Type {
case "payment_intent.succeeded": // update order to paid
case "payment_intent.payment_failed": // mark as failed
}

// ── CREATE ORDER (transaction) ─────────────────────────────────
tx := db.Begin()
defer func() { if r := recover(); r != nil { tx.Rollback() } }()
tx.Create(&order)
for _, item := range cartItems {
    tx.Create(&models.OrderItem{...})
    tx.Model(&Product{}).Where("id=?", item.ProductID).
        Update("stock", gorm.Expr("stock - ?", item.Quantity))
}
tx.Where("user_id=?", userID).Delete(&CartItem{})
tx.Commit()

// ── PRODUCT FILTER QUERY ───────────────────────────────────────
q := db.Model(&Product{}).Where("is_active=?", true).Preload("Category")
if search != "" { q = q.Where("name ILIKE ?", "%"+search+"%") }
if categoryID > 0 { q = q.Where("category_id=?", categoryID) }
if minPrice > 0 { q = q.Where("price>=?", minPrice) }
q.Count(&total)
q.Order("created_at DESC").Limit(limit).Offset(offset).Find(&products)
```

---

## Resources

- [Stripe Go SDK](https://github.com/stripe/stripe-go)
- [Stripe Test Cards](https://stripe.com/docs/testing)
- [GORM Transactions](https://gorm.io/docs/transactions.html)
- [Echo Framework](https://echo.labstack.com/)
- [go-redis Docs](https://redis.uptrace.dev/)

---
