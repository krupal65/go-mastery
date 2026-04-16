# 🐹 Go Language — Phase 2 Study Notes

> Complete notes for:
> - **Topic 1: Basic CRUD**
> - **Topic 2: Using GORM ORM**
> - **Topic 3: Models, Migrations, Relationships**
> - **Topic 4: CRUD with GORM**
> - **Topic 5: Environment Variables & Config**
> - **Topic 6: os.Getenv, .env files with godotenv**
> - **Topic 7: Error Handling & Logging**
> - **Topic 8: Centralized Error Handling**

---

## 📚 Table of Contents

- [Topic 1: Basic CRUD](#topic-1-basic-crud)
- [Topic 2: Using GORM ORM](#topic-2-using-gorm-orm)
- [Topic 3: Models, Migrations, Relationships](#topic-3-models-migrations-relationships)
- [Topic 4: CRUD with GORM](#topic-4-crud-with-gorm)
- [Topic 5: Environment Variables & Config](#topic-5-environment-variables--config)
- [Topic 6: os.Getenv, .env files with godotenv](#topic-6-osgetenv-env-files-with-godotenv)
- [Topic 7: Error Handling & Logging](#topic-7-error-handling--logging)
- [Topic 8: Centralized Error Handling](#topic-8-centralized-error-handling)
- [Interview Questions](#interview-questions)
- [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Topic 1: Basic CRUD

### What is CRUD?

**CRUD** = Create, Read, Update, Delete — the four fundamental operations for any data-driven application.

| Operation | HTTP Method | SQL | Description |
|---|---|---|---|
| **C**reate | POST | INSERT | Add new record |
| **R**ead | GET | SELECT | Fetch record(s) |
| **U**pdate | PUT / PATCH | UPDATE | Modify record |
| **D**elete | DELETE | DELETE | Remove record |

### Basic CRUD with database/sql (Raw SQL)

```go
package main

import (
    "database/sql"
    "log"
    _ "github.com/lib/pq"
)

type Product struct {
    ID       int     `json:"id"`
    Name     string  `json:"name"`
    Price    float64 `json:"price"`
    Stock    int     `json:"stock"`
}

// ── CREATE ────────────────────────────────────────────────────
func createProduct(db *sql.DB, p Product) (Product, error) {
    err := db.QueryRow(
        `INSERT INTO products (name, price, stock)
         VALUES ($1, $2, $3)
         RETURNING id, name, price, stock`,
        p.Name, p.Price, p.Stock,
    ).Scan(&p.ID, &p.Name, &p.Price, &p.Stock)
    return p, err
}

// ── READ ALL ──────────────────────────────────────────────────
func getProducts(db *sql.DB) ([]Product, error) {
    rows, err := db.Query("SELECT id, name, price, stock FROM products")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var products []Product
    for rows.Next() {
        var p Product
        if err := rows.Scan(&p.ID, &p.Name, &p.Price, &p.Stock); err != nil {
            return nil, err
        }
        products = append(products, p)
    }
    return products, rows.Err()
}

// ── READ ONE ──────────────────────────────────────────────────
func getProductByID(db *sql.DB, id int) (Product, error) {
    var p Product
    err := db.QueryRow(
        "SELECT id, name, price, stock FROM products WHERE id = $1", id,
    ).Scan(&p.ID, &p.Name, &p.Price, &p.Stock)
    return p, err   // returns sql.ErrNoRows if not found
}

// ── UPDATE ────────────────────────────────────────────────────
func updateProduct(db *sql.DB, id int, p Product) (Product, error) {
    err := db.QueryRow(
        `UPDATE products SET name=$1, price=$2, stock=$3
         WHERE id=$4
         RETURNING id, name, price, stock`,
        p.Name, p.Price, p.Stock, id,
    ).Scan(&p.ID, &p.Name, &p.Price, &p.Stock)
    return p, err
}

// ── DELETE ────────────────────────────────────────────────────
func deleteProduct(db *sql.DB, id int) error {
    result, err := db.Exec("DELETE FROM products WHERE id = $1", id)
    if err != nil {
        return err
    }
    rows, _ := result.RowsAffected()
    if rows == 0 {
        return sql.ErrNoRows
    }
    return nil
}
```

---

## Topic 2: Using GORM ORM

### What is an ORM?

**ORM** (Object Relational Mapper) maps Go structs to database tables so you write Go code instead of raw SQL. GORM is the most popular ORM in Go.

### GORM vs Raw SQL

| Feature | Raw SQL | GORM |
|---|---|---|
| Write SQL | Manual | Auto-generated |
| Table creation | Manual SQL | Auto-migrate |
| Relationships | Manual JOINs | `Preload`, associations |
| Learning curve | SQL knowledge needed | Go struct knowledge |
| Flexibility | Full control | Slightly less |
| Speed | Faster | Slightly slower |
| Best for | Complex queries, performance | Rapid development |

### Installation

```bash
go get gorm.io/gorm
go get gorm.io/driver/postgres   # PostgreSQL driver for GORM
```

### Connecting with GORM

```go
package main

import (
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

var DB *gorm.DB

func ConnectDB() {
    dsn := "postgresql://postgres:secret@localhost:5432/myapp?sslmode=disable"

    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Info), // log all SQL queries
    })
    if err != nil {
        log.Fatal("Failed to connect to database:", err)
    }

    // Configure connection pool (same as database/sql)
    sqlDB, _ := db.DB()
    sqlDB.SetMaxOpenConns(25)
    sqlDB.SetMaxIdleConns(10)
    sqlDB.SetConnMaxLifetime(5 * time.Minute)

    DB = db
    log.Println("Database connected!")
}
```

### GORM Model

```go
import "gorm.io/gorm"

// gorm.Model adds: ID, CreatedAt, UpdatedAt, DeletedAt (soft delete)
type User struct {
    gorm.Model                        // adds ID, CreatedAt, UpdatedAt, DeletedAt
    Name     string `gorm:"not null"`
    Email    string `gorm:"uniqueIndex;not null"`
    Age      int
}

// Custom model without gorm.Model
type Product struct {
    ID        uint      `gorm:"primaryKey;autoIncrement"`
    Name      string    `gorm:"size:100;not null"`
    Price     float64   `gorm:"not null"`
    Stock     int       `gorm:"default:0"`
    CreatedAt time.Time
    UpdatedAt time.Time
}
```

---

## Topic 3: Models, Migrations, Relationships

### GORM Model Tags

```go
type User struct {
    ID        uint      `gorm:"primaryKey;autoIncrement"`
    Name      string    `gorm:"size:100;not null"`
    Email     string    `gorm:"size:255;uniqueIndex;not null"`
    Password  string    `gorm:"size:255;not null"`
    Age       int       `gorm:"check:age >= 0"`
    Role      string    `gorm:"size:20;default:'user'"`
    IsActive  bool      `gorm:"default:true"`
    Bio       string    `gorm:"type:text"`
    CreatedAt time.Time
    UpdatedAt time.Time
    DeletedAt gorm.DeletedAt `gorm:"index"`  // soft delete
}
```

### Common GORM Tags

| Tag | Description | Example |
|---|---|---|
| `primaryKey` | Mark as primary key | `gorm:"primaryKey"` |
| `autoIncrement` | Auto increment | `gorm:"autoIncrement"` |
| `uniqueIndex` | Unique constraint | `gorm:"uniqueIndex"` |
| `index` | Regular index | `gorm:"index"` |
| `not null` | NOT NULL constraint | `gorm:"not null"` |
| `size:N` | Column size | `gorm:"size:255"` |
| `default:V` | Default value | `gorm:"default:0"` |
| `type:T` | Column type | `gorm:"type:text"` |
| `column:name` | Custom column name | `gorm:"column:user_name"` |
| `check:expr` | Check constraint | `gorm:"check:age >= 0"` |
| `-` | Ignore field | `gorm:"-"` |

### Auto Migration

```go
// AutoMigrate creates tables and adds missing columns automatically
// It does NOT delete columns or change existing column types

func migrate(db *gorm.DB) {
    err := db.AutoMigrate(
        &User{},
        &Product{},
        &Order{},
        &OrderItem{},
    )
    if err != nil {
        log.Fatal("Migration failed:", err)
    }
    log.Println("Migration completed!")
}

// Call in main.go
func main() {
    ConnectDB()
    migrate(DB)
    // ...
}
```

### Relationships

#### One-to-Many (User has many Posts)

```go
type User struct {
    gorm.Model
    Name  string
    Email string
    Posts []Post   // one user has many posts
}

type Post struct {
    gorm.Model
    Title   string
    Content string
    UserID  uint   // foreign key — MUST match User's primary key type
    User    User   // belongs to User (optional — for preloading)
}

// GORM convention: UserID is auto-recognized as foreign key for User
// AutoMigrate will add the foreign key constraint automatically
```

#### Many-to-Many (Students and Courses)

```go
type Student struct {
    gorm.Model
    Name    string
    Courses []Course `gorm:"many2many:student_courses;"` // join table name
}

type Course struct {
    gorm.Model
    Title    string
    Students []Student `gorm:"many2many:student_courses;"`
}

// GORM creates the student_courses join table automatically
```

#### One-to-One (User has one Profile)

```go
type User struct {
    gorm.Model
    Name    string
    Profile Profile   // one-to-one
}

type Profile struct {
    gorm.Model
    Bio    string
    Avatar string
    UserID uint   // foreign key
}
```

---

## Topic 4: CRUD with GORM

### Create

```go
// ── Create single record ───────────────────────────────────────
user := User{Name: "Rahul", Email: "rahul@example.com"}
result := db.Create(&user)

if result.Error != nil {
    log.Println("Error:", result.Error)
}
fmt.Println("Created ID:", user.ID)          // auto-filled
fmt.Println("Rows affected:", result.RowsAffected)

// ── Create multiple records ────────────────────────────────────
users := []User{
    {Name: "Rahul", Email: "rahul@example.com"},
    {Name: "Priya", Email: "priya@example.com"},
    {Name: "Arjun", Email: "arjun@example.com"},
}
db.Create(&users)

// ── Create with selected fields only ─────────────────────────
db.Select("Name", "Email").Create(&user)
// Omit specific fields
db.Omit("Age", "Role").Create(&user)
```

### Read

```go
// ── Find all records ───────────────────────────────────────────
var users []User
db.Find(&users)

// ── Find by primary key ────────────────────────────────────────
var user User
db.First(&user, 1)               // SELECT * FROM users WHERE id=1 LIMIT 1
db.First(&user, "id = ?", 1)    // same result

// First returns error if not found:
result := db.First(&user, 99)
if result.Error != nil {
    if errors.Is(result.Error, gorm.ErrRecordNotFound) {
        // user not found — return 404
    }
}

// ── Find with conditions ───────────────────────────────────────
var users []User
db.Where("name = ?", "Rahul").Find(&users)
db.Where("age > ? AND is_active = ?", 18, true).Find(&users)
db.Where("email LIKE ?", "%@gmail.com").Find(&users)

// ── Find one with condition ────────────────────────────────────
var user User
db.Where("email = ?", "rahul@example.com").First(&user)

// ── Order, Limit, Offset ──────────────────────────────────────
db.Order("created_at DESC").Limit(10).Offset(20).Find(&users)

// ── Select specific columns ────────────────────────────────────
db.Select("id", "name", "email").Find(&users)

// ── Count ─────────────────────────────────────────────────────
var count int64
db.Model(&User{}).Where("is_active = ?", true).Count(&count)
```

### Preloading (Eager Loading Relationships)

```go
// Load user WITH all their posts
var user User
db.Preload("Posts").First(&user, 1)
// user.Posts is now populated

// Load all users with their posts
var users []User
db.Preload("Posts").Find(&users)

// Nested preload — posts with their comments
db.Preload("Posts.Comments").First(&user, 1)

// Multiple preloads
db.Preload("Posts").Preload("Profile").First(&user, 1)
```

### Update

```go
// ── Update specific fields ─────────────────────────────────────
db.Model(&user).Update("Name", "Rahul Kumar")

// ── Update multiple fields with map ───────────────────────────
db.Model(&user).Updates(map[string]interface{}{
    "name":  "Rahul Kumar",
    "email": "rahulkumar@example.com",
    "age":   26,
})

// ── Update with struct (zero values are ignored!) ─────────────
db.Model(&user).Updates(User{Name: "Rahul", Age: 26})
// ⚠️ Age=0 would be IGNORED — use map for zero values

// ── Save — updates ALL fields including zero values ───────────
user.Name = "New Name"
user.Age = 0   // this WILL be saved with Save
db.Save(&user)

// ── Update with condition ─────────────────────────────────────
db.Model(&User{}).Where("is_active = ?", false).Update("role", "inactive")
```

### Delete

```go
// ── Soft delete (gorm.Model has DeletedAt) ─────────────────────
db.Delete(&user)
// Record is NOT removed — DeletedAt is set to current time
// Future queries will automatically exclude soft-deleted records

// ── Hard delete (permanently remove) ──────────────────────────
db.Unscoped().Delete(&user)

// ── Delete with condition ─────────────────────────────────────
db.Where("email = ?", "test@test.com").Delete(&User{})

// ── Delete by ID ──────────────────────────────────────────────
db.Delete(&User{}, 1)
db.Delete(&User{}, []int{1, 2, 3})   // delete multiple

// ── Include soft-deleted in query ────────────────────────────
db.Unscoped().Where("name = ?", "Rahul").Find(&users)
```

### GORM with Echo — Full Handler Example

```go
type UserHandler struct {
    db *gorm.DB
}

func NewUserHandler(db *gorm.DB) *UserHandler {
    return &UserHandler{db: db}
}

func (h *UserHandler) GetUsers(c echo.Context) error {
    var users []User
    if err := h.db.Find(&users).Error; err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not fetch users",
        })
    }
    return c.JSON(http.StatusOK, users)
}

func (h *UserHandler) CreateUser(c echo.Context) error {
    var user User
    if err := c.Bind(&user); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid body",
        })
    }
    if err := h.db.Create(&user).Error; err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not create user",
        })
    }
    return c.JSON(http.StatusCreated, user)
}

func (h *UserHandler) GetUserByID(c echo.Context) error {
    id := c.Param("id")
    var user User
    if err := h.db.First(&user, id).Error; err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return c.JSON(http.StatusNotFound, map[string]string{
                "error": "user not found",
            })
        }
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "db error",
        })
    }
    return c.JSON(http.StatusOK, user)
}
```

---

## Topic 5: Environment Variables & Config

### Why Environment Variables?

Never hardcode sensitive values in your code:
- Database credentials
- API keys and secrets
- JWT secret keys
- External service URLs

Using environment variables lets you change configuration without changing code and keeps secrets out of version control.

### Config Struct Pattern

```go
// config/config.go
package config

import (
    "fmt"
    "os"
    "strconv"
)

type Config struct {
    // Server
    ServerPort string
    AppEnv     string   // "development", "staging", "production"

    // Database
    DBHost     string
    DBPort     string
    DBUser     string
    DBPassword string
    DBName     string
    DBSSLMode  string

    // JWT
    JWTSecret     string
    JWTExpireHours int

    // External services
    SMTPHost  string
    SMTPPort  string
    SMTPUser  string
    SMTPPass  string
}

// Load reads all env vars and returns a Config
func Load() *Config {
    return &Config{
        // Server
        ServerPort: getEnv("SERVER_PORT", "8080"),
        AppEnv:     getEnv("APP_ENV", "development"),

        // Database
        DBHost:     getEnv("DB_HOST", "localhost"),
        DBPort:     getEnv("DB_PORT", "5432"),
        DBUser:     getEnv("DB_USER", "postgres"),
        DBPassword: mustGetEnv("DB_PASSWORD"),       // required — panics if missing
        DBName:     getEnv("DB_NAME", "myapp"),
        DBSSLMode:  getEnv("DB_SSLMODE", "disable"),

        // JWT
        JWTSecret:      mustGetEnv("JWT_SECRET"),
        JWTExpireHours: getEnvAsInt("JWT_EXPIRE_HOURS", 24),

        // SMTP
        SMTPHost: getEnv("SMTP_HOST", ""),
        SMTPPort: getEnv("SMTP_PORT", "587"),
        SMTPUser: getEnv("SMTP_USER", ""),
        SMTPPass: getEnv("SMTP_PASS", ""),
    }
}

// ── Helper functions ───────────────────────────────────────────

// getEnv returns env var or a default value
func getEnv(key, defaultVal string) string {
    if val := os.Getenv(key); val != "" {
        return val
    }
    return defaultVal
}

// mustGetEnv panics if the env var is not set — for required values
func mustGetEnv(key string) string {
    val := os.Getenv(key)
    if val == "" {
        panic(fmt.Sprintf("required environment variable %s is not set", key))
    }
    return val
}

// getEnvAsInt returns env var as int or default
func getEnvAsInt(key string, defaultVal int) int {
    valStr := os.Getenv(key)
    if val, err := strconv.Atoi(valStr); err == nil {
        return val
    }
    return defaultVal
}

// getEnvAsBool returns env var as bool or default
func getEnvAsBool(key string, defaultVal bool) bool {
    valStr := os.Getenv(key)
    if val, err := strconv.ParseBool(valStr); err == nil {
        return val
    }
    return defaultVal
}

// DSN builds the PostgreSQL connection string from config
func (c *Config) DSN() string {
    return fmt.Sprintf(
        "postgresql://%s:%s@%s:%s/%s?sslmode=%s",
        c.DBUser, c.DBPassword, c.DBHost, c.DBPort, c.DBName, c.DBSSLMode,
    )
}
```

---

## Topic 6: os.Getenv, .env files with godotenv

### os.Getenv — Reading Environment Variables

```go
import "os"

// Read single env var — returns "" if not set
port := os.Getenv("PORT")                // "8080" or ""

// Set env var (in-process only)
os.Setenv("APP_ENV", "testing")

// Unset env var
os.Unsetenv("APP_ENV")

// LookupEnv — returns value AND whether it was set
val, exists := os.LookupEnv("DB_PASSWORD")
if !exists {
    log.Fatal("DB_PASSWORD is not set!")
}

// Get all environment variables
for _, env := range os.Environ() {
    fmt.Println(env)   // "KEY=VALUE"
}
```

### .env File with godotenv

```bash
go get github.com/joho/godotenv
```

```bash
# .env file — NEVER commit to git!
# Add .env to your .gitignore

SERVER_PORT=8080
APP_ENV=development

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=mysecretpassword
DB_NAME=myapp
DB_SSLMODE=disable

JWT_SECRET=my-super-secret-jwt-key-change-in-production
JWT_EXPIRE_HOURS=24

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=myemail@gmail.com
SMTP_PASS=myapppassword
```

```go
import "github.com/joho/godotenv"

// Load .env file — call at very start of main()
func main() {
    // Load .env — ignore error in production (vars set by system)
    if err := godotenv.Load(); err != nil {
        log.Println("No .env file found — using system environment")
    }

    // Now os.Getenv works for vars from .env
    cfg := config.Load()

    // ...
}

// Load specific file
godotenv.Load(".env.local")
godotenv.Load(".env.test")

// Overload — overwrites existing env vars
godotenv.Overload(".env.override")
```

### Environment-Specific Files

```
project/
├── .env            ← base config (committed — no secrets)
├── .env.local      ← local overrides (NOT committed)
├── .env.test       ← test environment (committed)
├── .env.example    ← template showing all keys (committed)
└── .gitignore      ← contains: .env.local, .env
```

```bash
# .env.example — commit this to show teammates what vars are needed
SERVER_PORT=
APP_ENV=
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=     # required — get from team lead
DB_NAME=
JWT_SECRET=      # required — generate with: openssl rand -base64 32
```

### Using Config in main.go — Complete Example

```go
package main

import (
    "log"
    "github.com/joho/godotenv"
    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"

    "myapp/config"
    "myapp/handlers"
)

func main() {
    // 1. Load environment variables
    godotenv.Load()

    // 2. Load config
    cfg := config.Load()
    log.Printf("Starting in %s mode on port %s", cfg.AppEnv, cfg.ServerPort)

    // 3. Connect to database
    db, err := gorm.Open(postgres.Open(cfg.DSN()), &gorm.Config{})
    if err != nil {
        log.Fatal("DB connection failed:", err)
    }

    // 4. Run migrations
    db.AutoMigrate(&models.User{}, &models.Product{})

    // 5. Setup Echo
    e := echo.New()
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())

    // 6. Setup handlers with dependencies
    h := handlers.NewUserHandler(db, cfg)

    // 7. Register routes
    api := e.Group("/api/v1")
    api.GET("/users",        h.GetUsers)
    api.POST("/users",       h.CreateUser)
    api.GET("/users/:id",    h.GetUserByID)
    api.PUT("/users/:id",    h.UpdateUser)
    api.DELETE("/users/:id", h.DeleteUser)

    // 8. Start server
    e.Logger.Fatal(e.Start(":" + cfg.ServerPort))
}
```

---

## Topic 7: Error Handling & Logging

### Go Error Handling Best Practices

```go
// ── Rule 1: Always handle errors immediately ───────────────────
user, err := getUser(id)
if err != nil {
    // handle it right here
    return err
}

// ── Rule 2: Wrap errors with context ──────────────────────────
func getUser(id int) (User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        return User{}, fmt.Errorf("getUser id=%d: %w", id, err)
        //                        ↑ adds context  ↑ wraps original
    }
    return user, nil
}

// ── Rule 3: Distinguish error types ───────────────────────────
var (
    ErrNotFound   = errors.New("not found")
    ErrForbidden  = errors.New("forbidden")
    ErrConflict   = errors.New("conflict")
)

func getUser(id int) (User, error) {
    if id <= 0 {
        return User{}, fmt.Errorf("getUser: %w", ErrNotFound)
    }
    // ...
}

// In handler
if errors.Is(err, ErrNotFound) {
    return c.JSON(http.StatusNotFound, ...)
}

// ── Rule 4: Log errors at the boundary (handler) ──────────────
func (h *UserHandler) GetUser(c echo.Context) error {
    user, err := h.service.GetUser(id)
    if err != nil {
        // Log here — only once, at the top level
        log.Printf("ERROR GetUser id=%d: %v", id, err)
        return c.JSON(http.StatusInternalServerError, ...)
    }
    return c.JSON(http.StatusOK, user)
}
```

### Standard log Package

```go
import "log"

// Basic logging — outputs to stderr
log.Println("Server starting on :8080")
log.Printf("User %d created successfully", user.ID)
log.Print("No newline here")

// Fatal — logs and calls os.Exit(1)
log.Fatal("Database connection failed:", err)
log.Fatalf("Port %s already in use", port)

// Panic — logs and calls panic()
log.Panic("unexpected nil pointer")

// Add timestamp prefix
log.SetFlags(log.LstdFlags | log.Lshortfile)
// Output: 2024/01/15 10:30:00 main.go:42: Server starting

// Custom prefix
log.SetPrefix("[MYAPP] ")
// Output: [MYAPP] 2024/01/15 10:30:00 Server starting
```

### Structured Logging with zerolog

```bash
go get github.com/rs/zerolog
```

```go
import (
    "github.com/rs/zerolog"
    "github.com/rs/zerolog/log"
    "os"
)

func setupLogger(env string) {
    zerolog.TimeFieldFormat = zerolog.TimeFormatUnix

    if env == "development" {
        // Pretty colored output for development
        log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})
    } else {
        // JSON output for production (easy to parse by log aggregators)
        log.Logger = zerolog.New(os.Stderr).With().Timestamp().Logger()
    }
}

// Usage
log.Info().Str("method", "GET").Str("path", "/users").Msg("request received")
log.Error().Err(err).Int("user_id", id).Msg("failed to fetch user")
log.Fatal().Err(err).Msg("database connection failed")
log.Debug().Interface("user", user).Msg("user details")

// With request context
log.Info().
    Str("request_id", requestID).
    Str("method", c.Request().Method).
    Str("path", c.Request().URL.Path).
    Int("status", 200).
    Dur("latency", time.Since(start)).
    Msg("request completed")
```

### Logging Middleware

```go
func loggingMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        start := time.Now()

        err := next(c)

        log.Info().
            Str("method",  c.Request().Method).
            Str("path",    c.Request().URL.Path).
            Int("status",  c.Response().Status).
            Dur("latency", time.Since(start)).
            Str("ip",      c.RealIP()).
            Msg("request")

        return err
    }
}
```

---

## Topic 8: Centralized Error Handling

### Why Centralize Error Handling?

Without centralized handling, every handler needs its own error formatting code. Centralized handling ensures:
- Consistent error response format across all endpoints
- One place to log all errors
- Easy to change error format for the whole API
- Handles unexpected panics gracefully

### Error Types

```go
// Define all application error types in one place
package apperr

import "net/http"

type AppError struct {
    StatusCode int    `json:"-"`           // HTTP status code
    Code       string `json:"code"`        // machine-readable code
    Message    string `json:"message"`     // human-readable message
    Details    any    `json:"details,omitempty"` // extra info
}

func (e *AppError) Error() string {
    return e.Message
}

// ── Constructor functions for common errors ───────────────────
func NotFound(msg string) *AppError {
    return &AppError{StatusCode: 404, Code: "NOT_FOUND", Message: msg}
}

func BadRequest(msg string) *AppError {
    return &AppError{StatusCode: 400, Code: "BAD_REQUEST", Message: msg}
}

func Unauthorized(msg string) *AppError {
    return &AppError{StatusCode: 401, Code: "UNAUTHORIZED", Message: msg}
}

func Forbidden(msg string) *AppError {
    return &AppError{StatusCode: 403, Code: "FORBIDDEN", Message: msg}
}

func Conflict(msg string) *AppError {
    return &AppError{StatusCode: 409, Code: "CONFLICT", Message: msg}
}

func ValidationFailed(details any) *AppError {
    return &AppError{
        StatusCode: 422,
        Code:       "VALIDATION_FAILED",
        Message:    "input validation failed",
        Details:    details,
    }
}

func Internal(msg string) *AppError {
    return &AppError{StatusCode: 500, Code: "INTERNAL_ERROR", Message: msg}
}
```

### Custom Echo Error Handler

```go
// middleware/error_handler.go
package middleware

import (
    "net/http"
    "github.com/labstack/echo/v4"
    "github.com/rs/zerolog/log"
    "myapp/apperr"
)

type ErrorResponse struct {
    Success bool   `json:"success"`
    Code    string `json:"code"`
    Message string `json:"message"`
    Details any    `json:"details,omitempty"`
}

func GlobalErrorHandler(err error, c echo.Context) {
    // ── Already sent? do nothing ──────────────────────────────
    if c.Response().Committed {
        return
    }

    status  := http.StatusInternalServerError
    code    := "INTERNAL_ERROR"
    message := "something went wrong"
    var details any

    // ── Handle our custom AppError ────────────────────────────
    var appErr *apperr.AppError
    if errors.As(err, &appErr) {
        status  = appErr.StatusCode
        code    = appErr.Code
        message = appErr.Message
        details = appErr.Details
    } else if he, ok := err.(*echo.HTTPError); ok {
        // ── Handle Echo built-in errors ───────────────────────
        status  = he.Code
        message = fmt.Sprintf("%v", he.Message)
        code    = "HTTP_ERROR"
    }

    // ── Log 5xx errors ────────────────────────────────────────
    if status >= 500 {
        log.Error().
            Err(err).
            Str("path",   c.Request().URL.Path).
            Str("method", c.Request().Method).
            Int("status", status).
            Msg("server error")
    }

    // ── Send error response ───────────────────────────────────
    c.JSON(status, ErrorResponse{
        Success: false,
        Code:    code,
        Message: message,
        Details: details,
    })
}

// Register in main.go
// e.HTTPErrorHandler = middleware.GlobalErrorHandler
```

### Using AppErrors in Handlers

```go
// handlers/user.go
func (h *UserHandler) GetUserByID(c echo.Context) error {
    id, err := strconv.Atoi(c.Param("id"))
    if err != nil {
        // return apperr — GlobalErrorHandler formats it
        return apperr.BadRequest("id must be a number")
    }

    var user models.User
    if err := h.db.First(&user, id).Error; err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return apperr.NotFound("user not found")
        }
        return apperr.Internal("could not fetch user")
    }

    return c.JSON(http.StatusOK, user)
}

func (h *UserHandler) CreateUser(c echo.Context) error {
    var req CreateUserRequest
    if err := c.Bind(&req); err != nil {
        return apperr.BadRequest("invalid request format")
    }
    if err := c.Validate(&req); err != nil {
        // Pass validation errors as details
        return apperr.ValidationFailed(err.Error())
    }

    user := models.User{Name: req.Name, Email: req.Email}
    if err := h.db.Create(&user).Error; err != nil {
        // Check for unique constraint violation
        if strings.Contains(err.Error(), "duplicate key") {
            return apperr.Conflict("email already registered")
        }
        return apperr.Internal("could not create user")
    }

    return c.JSON(http.StatusCreated, user)
}
```

### Panic Recovery Middleware

```go
// Custom recovery middleware with logging
func RecoveryMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        defer func() {
            if r := recover(); r != nil {
                err, ok := r.(error)
                if !ok {
                    err = fmt.Errorf("panic: %v", r)
                }

                // Log the panic with stack trace
                log.Error().
                    Err(err).
                    Str("path",   c.Request().URL.Path).
                    Str("method", c.Request().Method).
                    Msg("panic recovered")

                c.JSON(http.StatusInternalServerError, ErrorResponse{
                    Success: false,
                    Code:    "PANIC",
                    Message: "internal server error",
                })
            }
        }()
        return next(c)
    }
}
```

### Complete main.go Bringing It All Together

```go
package main

import (
    "log"
    "github.com/joho/godotenv"
    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"

    "myapp/config"
    "myapp/handlers"
    appmiddleware "myapp/middleware"
    "myapp/models"
)

func main() {
    // ── 1. Load environment ────────────────────────────────────
    godotenv.Load()
    cfg := config.Load()

    // ── 2. Setup logger ────────────────────────────────────────
    setupLogger(cfg.AppEnv)

    // ── 3. Connect DB ──────────────────────────────────────────
    db, err := gorm.Open(postgres.Open(cfg.DSN()), &gorm.Config{})
    if err != nil {
        log.Fatal("DB failed:", err)
    }

    // ── 4. Run migrations ──────────────────────────────────────
    db.AutoMigrate(&models.User{}, &models.Product{})

    // ── 5. Setup Echo ──────────────────────────────────────────
    e := echo.New()
    e.HideBanner = true

    // ── 6. Global error handler ────────────────────────────────
    e.HTTPErrorHandler = appmiddleware.GlobalErrorHandler

    // ── 7. Middleware ──────────────────────────────────────────
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())
    e.Use(middleware.CORS())

    // ── 8. Routes ──────────────────────────────────────────────
    h := handlers.NewUserHandler(db, cfg)
    api := e.Group("/api/v1")
    api.GET("/users",        h.GetUsers)
    api.POST("/users",       h.CreateUser)
    api.GET("/users/:id",    h.GetUserByID)
    api.PUT("/users/:id",    h.UpdateUser)
    api.DELETE("/users/:id", h.DeleteUser)

    // ── 9. Start server ────────────────────────────────────────
    log.Printf("Server starting on :%s in %s mode", cfg.ServerPort, cfg.AppEnv)
    e.Logger.Fatal(e.Start(":" + cfg.ServerPort))
}
```

---

## Interview Questions

### Topic 1 & 2: Basic CRUD & GORM

**Q: What is an ORM and why use GORM?**
> ORM (Object Relational Mapper) maps Go structs to database tables so you write Go instead of SQL. GORM provides auto-migration, relationships, hooks, and a fluent API. It speeds up development but raw SQL is better for complex queries and maximum performance.

**Q: What does gorm.Model give you?**
> It embeds `ID uint`, `CreatedAt time.Time`, `UpdatedAt time.Time`, and `DeletedAt gorm.DeletedAt` into your struct. ID is auto-increment primary key. DeletedAt enables soft delete — records are marked deleted instead of removed from the DB.

**Q: What is the difference between db.Save and db.Updates?**
> `db.Save` updates ALL fields including zero values (Age=0 will be saved as 0). `db.Updates` with a struct ignores zero-value fields. `db.Updates` with a `map[string]interface{}` updates only the specified keys. Use map when you need to set a field to zero.

### Topic 3: Models, Migrations, Relationships

**Q: What does AutoMigrate do and what are its limitations?**
> AutoMigrate creates tables for structs that don't exist and adds new columns. It does NOT delete columns, change column types, or rename columns. For production schema changes use a migration tool like `golang-migrate` for full control.

**Q: How does GORM handle One-to-Many relationships?**
> Define the slice in the parent: `Posts []Post` and the foreign key in the child: `UserID uint`. GORM convention auto-recognizes `UserID` as the foreign key for `User`. Use `db.Preload("Posts").Find(&users)` to load the relationship.

**Q: What is soft delete in GORM?**
> When a struct embeds `gorm.Model` (which has `DeletedAt gorm.DeletedAt`), calling `db.Delete()` sets `DeletedAt` to the current time instead of removing the row. All subsequent queries automatically filter out soft-deleted records. Use `db.Unscoped()` to include them.

### Topic 5 & 6: Environment Variables

**Q: Why should you never hardcode credentials in code?**
> Credentials in code get committed to version control and are visible to everyone with repo access. If the repo is public, credentials are exposed to the entire internet. Use environment variables — set them in `.env` for local dev and in the system/cloud for production.

**Q: What is the difference between os.Getenv and os.LookupEnv?**
> `os.Getenv` returns an empty string if the variable is not set — you can't distinguish "not set" from "set to empty string". `os.LookupEnv` returns the value AND a bool indicating whether it was set. Use `LookupEnv` for required variables.

**Q: What does godotenv.Load() do?**
> It reads a `.env` file and sets each key-value pair as an environment variable using `os.Setenv`. This only affects the current process. It does NOT override variables that are already set in the system environment.

### Topic 7 & 8: Error Handling & Logging

**Q: What is the difference between log.Fatal and log.Panic?**
> Both log the message. `log.Fatal` calls `os.Exit(1)` — deferred functions do NOT run. `log.Panic` calls `panic()` — deferred functions DO run and the panic can be recovered. Use Fatal for startup failures, avoid in request handlers.

**Q: Why use structured logging (zerolog) over fmt.Println?**
> Structured logs output JSON, making them machine-parseable by log aggregators (Datadog, ELK, CloudWatch). They support log levels (debug, info, error), contextual fields (user_id, request_id), and are much faster than fmt-based logging.

**Q: What is centralized error handling in Echo?**
> Setting `e.HTTPErrorHandler = myHandler` gives one function that handles ALL errors returned from handlers. Instead of formatting error responses in every handler, you return an error and the central handler formats it consistently. Ensures uniform error response shape across all endpoints.

**Q: Why log errors only at the handler level, not in service/DB layer?**
> If every layer logs the error, the same error appears multiple times in logs — once per layer. The handler is the boundary between your code and the client, so log once there with full context (request path, user ID, etc.). Lower layers should wrap and return errors, not log them.

---

## Quick Reference Cheatsheet

```go
// ── GORM SETUP ─────────────────────────────────────────────────
db, _ := gorm.Open(postgres.Open(dsn), &gorm.Config{})
db.AutoMigrate(&User{}, &Product{})

// ── GORM MODEL ─────────────────────────────────────────────────
type User struct {
    gorm.Model                              // ID, CreatedAt, UpdatedAt, DeletedAt
    Name  string `gorm:"size:100;not null"`
    Email string `gorm:"uniqueIndex;not null"`
}

// ── GORM CRUD ──────────────────────────────────────────────────
db.Create(&user)                            // INSERT
db.Find(&users)                             // SELECT all
db.First(&user, id)                         // SELECT by PK
db.Where("email = ?", email).First(&user)  // SELECT with condition
db.Model(&user).Updates(map[string]any{})  // UPDATE specific fields
db.Save(&user)                             // UPDATE all fields
db.Delete(&user)                           // soft DELETE
db.Unscoped().Delete(&user)                // hard DELETE
db.Preload("Posts").Find(&users)           // load relations

// gorm.ErrRecordNotFound — check when First returns error

// ── CONFIG ─────────────────────────────────────────────────────
godotenv.Load()                 // load .env file
os.Getenv("DB_HOST")           // read env var
os.LookupEnv("DB_PASSWORD")   // read + check if set

// ── LOGGING ───────────────────────────────────────────────────
log.Println("message")          // standard log
log.Fatal("critical", err)      // log + os.Exit(1)

// zerolog
log.Info().Str("key","val").Msg("message")
log.Error().Err(err).Int("id", id).Msg("failed")

// ── CENTRALIZED ERROR HANDLER ─────────────────────────────────
e.HTTPErrorHandler = func(err error, c echo.Context) {
    var appErr *apperr.AppError
    if errors.As(err, &appErr) {
        c.JSON(appErr.StatusCode, appErr)
        return
    }
    c.JSON(500, map[string]string{"error": "internal server error"})
}

// ── APP ERRORS ────────────────────────────────────────────────
return apperr.NotFound("user not found")      // 404
return apperr.BadRequest("invalid id")        // 400
return apperr.Unauthorized("login required")  // 401
return apperr.Conflict("email taken")         // 409
return apperr.Internal("db error")            // 500
```

---

## Resources

- [GORM Official Docs](https://gorm.io/docs/)
- [godotenv GitHub](https://github.com/joho/godotenv)
- [zerolog GitHub](https://github.com/rs/zerolog)
- [go-playground/validator](https://github.com/go-playground/validator)
- [Echo Error Handling](https://echo.labstack.com/docs/error-handling)

---

*Phase 2 — GORM · Config · Error Handling · Logging — All 8 Topics Covered ✅*