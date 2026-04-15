# 🐹 Go Language — Phase 2 Study Notes (Days 8–14)

> Complete notes for the **Remaining 5 Topics of Phase 2:**
> - **Topic 7: Request Handling & Validation**
> - **Topic 8: Path Params, Query Params, Request Body**
> - **Topic 9: Input Validation**
> - **Topic 10: Connecting to PostgreSQL**
> - **Topic 11: database/sql & lib/pq Driver**

---

## 📚 Table of Contents

- [Topic 7: Request Handling & Validation](#topic-7-request-handling--validation)
- [Topic 8: Path Params, Query Params, Request Body](#topic-8-path-params-query-params-request-body)
- [Topic 9: Input Validation](#topic-9-input-validation)
- [Topic 10: Connecting to PostgreSQL](#topic-10-connecting-to-postgresql)
- [Topic 11: database/sql & lib/pq Driver](#topic-11-databasesql--libpq-driver)
- [Interview Questions](#interview-questions)
- [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Topic 7: Request Handling & Validation

### What is Request Handling?

Request handling means reading and processing everything that comes in with an HTTP request — the URL path, query string, headers, and body — and responding appropriately.

### Full Request Lifecycle in Echo

```
Client sends HTTP request
        ↓
Global Middleware runs (Logger, Recover, CORS)
        ↓
Route matched by Echo router
        ↓
Route-level Middleware runs (Auth, RateLimit)
        ↓
Handler function called with echo.Context
        ↓
Handler reads params / body / headers
        ↓
Handler validates input
        ↓
Handler calls service / DB layer
        ↓
Handler writes JSON response
        ↓
Response sent back to client
```

### Handler Structure Best Practice

```go
// Always follow this structure inside a handler:
// 1. Read / Bind input
// 2. Validate input
// 3. Call business logic
// 4. Return response

func createUserHandler(c echo.Context) error {
    // ── Step 1: Bind ─────────────────────────────────────────
    var req CreateUserRequest
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, ErrorResponse{
            Error: "invalid request format",
        })
    }

    // ── Step 2: Validate ──────────────────────────────────────
    if err := c.Validate(&req); err != nil {
        return c.JSON(http.StatusUnprocessableEntity, ErrorResponse{
            Error: err.Error(),
        })
    }

    // ── Step 3: Business logic ────────────────────────────────
    user, err := userService.Create(req)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, ErrorResponse{
            Error: "could not create user",
        })
    }

    // ── Step 4: Response ─────────────────────────────────────
    return c.JSON(http.StatusCreated, user)
}
```

### Standardized API Response

```go
// Always return consistent response shapes
type APIResponse struct {
    Success bool        `json:"success"`
    Message string      `json:"message,omitempty"`
    Data    interface{} `json:"data,omitempty"`
}

type ErrorResponse struct {
    Success bool   `json:"success"`
    Error   string `json:"error"`
    Code    int    `json:"code,omitempty"`
}

// Helper functions
func successResponse(c echo.Context, status int, data interface{}) error {
    return c.JSON(status, APIResponse{Success: true, Data: data})
}

func errorResponse(c echo.Context, status int, msg string) error {
    return c.JSON(status, ErrorResponse{Success: false, Error: msg})
}

// Usage
return successResponse(c, http.StatusOK, users)
return errorResponse(c, http.StatusNotFound, "user not found")
```

### Custom Echo Error Handler

```go
// Centralized error handling — handles ALL unhandled errors
func customErrorHandler(err error, c echo.Context) {
    code := http.StatusInternalServerError
    message := "internal server error"

    // Check if it's an echo HTTP error
    if he, ok := err.(*echo.HTTPError); ok {
        code = he.Code
        message = fmt.Sprintf("%v", he.Message)
    }

    c.JSON(code, ErrorResponse{
        Success: false,
        Error:   message,
        Code:    code,
    })
}

// Register in main
e := echo.New()
e.HTTPErrorHandler = customErrorHandler
```

---

## Topic 8: Path Params, Query Params, Request Body

### Path Parameters

Path parameters are **part of the URL path** — they identify a specific resource.

```go
// Define route with path parameter
e.GET("/users/:id", getUserByID)
e.GET("/users/:userID/posts/:postID", getUserPost)

// ── Reading path params ────────────────────────────────────────
func getUserByID(c echo.Context) error {
    // Always returns a string — convert as needed
    idStr := c.Param("id")

    // Convert to int
    id, err := strconv.Atoi(idStr)
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "id must be a number",
        })
    }

    // Fetch user...
    return c.JSON(http.StatusOK, map[string]int{"id": id})
}

// ── Multiple path params ───────────────────────────────────────
func getUserPost(c echo.Context) error {
    userID, _ := strconv.Atoi(c.Param("userID"))
    postID, _ := strconv.Atoi(c.Param("postID"))

    return c.JSON(http.StatusOK, map[string]int{
        "user_id": userID,
        "post_id": postID,
    })
}
```

### Query Parameters

Query parameters come **after the `?`** in the URL — used for filtering, sorting, pagination.

```go
// URL: GET /users?page=2&limit=10&sort=name&search=rahul&active=true

e.GET("/users", getUsers)

func getUsers(c echo.Context) error {
    // ── Basic query param ─────────────────────────────────────
    page  := c.QueryParam("page")    // "2" (string)
    limit := c.QueryParam("limit")   // "10" (string)
    sort  := c.QueryParam("sort")    // "name"
    search := c.QueryParam("search") // "rahul"

    // ── With default values ───────────────────────────────────
    if page  == "" { page  = "1"  }
    if limit == "" { limit = "10" }
    if sort  == "" { sort  = "id" }

    // ── Convert types ─────────────────────────────────────────
    pageInt,  _ := strconv.Atoi(page)
    limitInt, _ := strconv.Atoi(limit)

    // ── Boolean query param ───────────────────────────────────
    activeStr := c.QueryParam("active")      // "true"
    active, _ := strconv.ParseBool(activeStr) // true

    return c.JSON(http.StatusOK, map[string]interface{}{
        "page":   pageInt,
        "limit":  limitInt,
        "sort":   sort,
        "search": search,
        "active": active,
    })
}
```

### Request Body — Bind & Read

```go
// ── Struct for request body ───────────────────────────────────
type CreateUserRequest struct {
    Name     string `json:"name"`
    Email    string `json:"email"`
    Age      int    `json:"age"`
    Password string `json:"password"`
}

// ── Bind JSON body ────────────────────────────────────────────
func createUser(c echo.Context) error {
    var req CreateUserRequest

    // c.Bind() reads Content-Type and decodes accordingly
    // Supports: JSON, XML, form data
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid request body: " + err.Error(),
        })
    }

    return c.JSON(http.StatusCreated, req)
}

// ── Raw body reading (when Bind is not enough) ────────────────
func rawBodyHandler(c echo.Context) error {
    body, err := io.ReadAll(c.Request().Body)
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "could not read body",
        })
    }
    defer c.Request().Body.Close()

    fmt.Println("Raw body:", string(body))
    return c.JSON(http.StatusOK, map[string]string{"received": string(body)})
}
```

### Reading Request Headers

```go
func headersHandler(c echo.Context) error {
    // Read specific header
    auth       := c.Request().Header.Get("Authorization")
    contentType := c.Request().Header.Get("Content-Type")
    userAgent  := c.Request().Header.Get("User-Agent")

    // Check if header exists
    if auth == "" {
        return c.JSON(http.StatusUnauthorized, map[string]string{
            "error": "Authorization header is required",
        })
    }

    // Strip "Bearer " prefix from token
    token := strings.TrimPrefix(auth, "Bearer ")

    return c.JSON(http.StatusOK, map[string]string{
        "token":        token,
        "content_type": contentType,
        "user_agent":   userAgent,
    })
}
```

### Combining All Input Types — Real Example

```go
// GET /api/v1/users/:id/posts?page=1&limit=5
func getUserPosts(c echo.Context) error {
    // Path param
    userID, err := strconv.Atoi(c.Param("id"))
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid user id",
        })
    }

    // Query params with defaults
    pageStr  := c.QueryParam("page")
    limitStr := c.QueryParam("limit")

    page,  _ := strconv.Atoi(pageStr)
    limit, _ := strconv.Atoi(limitStr)
    if page  <= 0 { page  = 1  }
    if limit <= 0 { limit = 10 }

    // Header
    token := c.Request().Header.Get("Authorization")
    if token == "" {
        return c.JSON(http.StatusUnauthorized, map[string]string{
            "error": "missing token",
        })
    }

    // Calculate offset
    offset := (page - 1) * limit

    return c.JSON(http.StatusOK, map[string]interface{}{
        "user_id": userID,
        "page":    page,
        "limit":   limit,
        "offset":  offset,
    })
}
```

---

## Topic 9: Input Validation

### Why Validate?

Never trust client input. Validation ensures:
- Required fields are present
- Values are in the correct format (email, phone)
- Numbers are in valid range
- Strings meet length requirements

### Setup go-playground/validator with Echo

```bash
go get github.com/go-playground/validator/v10
```

```go
// ── Setup validator ───────────────────────────────────────────
import "github.com/go-playground/validator/v10"

// Create a custom validator wrapper
type CustomValidator struct {
    validator *validator.Validate
}

func (cv *CustomValidator) Validate(i interface{}) error {
    if err := cv.validator.Struct(i); err != nil {
        return echo.NewHTTPError(http.StatusUnprocessableEntity, err.Error())
    }
    return nil
}

// Register in main.go
func main() {
    e := echo.New()
    e.Validator = &CustomValidator{validator: validator.New()}
    // ...
}
```

### Validation Tags

```go
type CreateUserRequest struct {
    // ── Required ──────────────────────────────────────────────
    Name  string `json:"name"  validate:"required"`
    Email string `json:"email" validate:"required,email"`

    // ── String length ─────────────────────────────────────────
    Username string `json:"username" validate:"required,min=3,max=20"`
    Password string `json:"password" validate:"required,min=8"`
    Bio      string `json:"bio"      validate:"max=200"`

    // ── Numbers ───────────────────────────────────────────────
    Age  int     `json:"age"  validate:"required,min=0,max=120"`
    Price float64 `json:"price" validate:"required,gt=0"`

    // ── Enums / specific values ───────────────────────────────
    Role   string `json:"role"   validate:"required,oneof=admin user moderator"`
    Status string `json:"status" validate:"required,oneof=active inactive"`

    // ── Optional fields ───────────────────────────────────────
    Phone string `json:"phone" validate:"omitempty,e164"`  // only validate if provided

    // ── URL ───────────────────────────────────────────────────
    Website string `json:"website" validate:"omitempty,url"`
}
```

### All Common Validation Tags

| Tag | Description | Example |
|---|---|---|
| `required` | Field must not be zero value | `validate:"required"` |
| `email` | Valid email format | `validate:"email"` |
| `min=N` | Min value (number) or min length (string) | `validate:"min=3"` |
| `max=N` | Max value (number) or max length (string) | `validate:"max=100"` |
| `gt=N` | Greater than N | `validate:"gt=0"` |
| `gte=N` | Greater than or equal | `validate:"gte=18"` |
| `lt=N` | Less than N | `validate:"lt=100"` |
| `lte=N` | Less than or equal | `validate:"lte=65"` |
| `len=N` | Exact length | `validate:"len=10"` |
| `oneof` | Value must be one of listed | `validate:"oneof=a b c"` |
| `url` | Valid URL | `validate:"url"` |
| `uuid` | Valid UUID | `validate:"uuid"` |
| `numeric` | Only numeric characters | `validate:"numeric"` |
| `alpha` | Only letters | `validate:"alpha"` |
| `alphanum` | Letters and numbers only | `validate:"alphanum"` |
| `omitempty` | Skip validation if field is empty | `validate:"omitempty,email"` |

### Human-Readable Validation Errors

```go
import (
    "github.com/go-playground/validator/v10"
    "strings"
)

// Convert validator errors to human-readable messages
func formatValidationErrors(err error) map[string]string {
    errors := map[string]string{}

    if validationErrors, ok := err.(validator.ValidationErrors); ok {
        for _, e := range validationErrors {
            field := strings.ToLower(e.Field())
            switch e.Tag() {
            case "required":
                errors[field] = field + " is required"
            case "email":
                errors[field] = field + " must be a valid email"
            case "min":
                errors[field] = fmt.Sprintf("%s must be at least %s characters", field, e.Param())
            case "max":
                errors[field] = fmt.Sprintf("%s must be at most %s characters", field, e.Param())
            case "oneof":
                errors[field] = fmt.Sprintf("%s must be one of: %s", field, e.Param())
            default:
                errors[field] = field + " is invalid"
            }
        }
    }
    return errors
}

// Usage in handler
func createUser(c echo.Context) error {
    var req CreateUserRequest
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid request body",
        })
    }
    if err := c.Validate(&req); err != nil {
        // Return detailed field-level errors
        if he, ok := err.(*echo.HTTPError); ok {
            if valErrs, ok := he.Message.(validator.ValidationErrors); ok {
                return c.JSON(http.StatusUnprocessableEntity, map[string]interface{}{
                    "error":  "validation failed",
                    "fields": formatValidationErrors(valErrs),
                })
            }
        }
        return c.JSON(http.StatusUnprocessableEntity, map[string]string{
            "error": err.Error(),
        })
    }

    // All valid — proceed
    return c.JSON(http.StatusCreated, req)
}
```

### Manual Validation (Without Library)

```go
func validateCreateUser(req CreateUserRequest) []string {
    var errs []string

    if strings.TrimSpace(req.Name) == "" {
        errs = append(errs, "name is required")
    }
    if len(req.Name) > 100 {
        errs = append(errs, "name must be 100 characters or less")
    }
    if req.Email == "" {
        errs = append(errs, "email is required")
    }
    if !strings.Contains(req.Email, "@") {
        errs = append(errs, "email format is invalid")
    }
    if req.Age < 0 || req.Age > 120 {
        errs = append(errs, "age must be between 0 and 120")
    }

    return errs
}

func createUser(c echo.Context) error {
    var req CreateUserRequest
    c.Bind(&req)

    if errs := validateCreateUser(req); len(errs) > 0 {
        return c.JSON(http.StatusUnprocessableEntity, map[string]interface{}{
            "error":  "validation failed",
            "errors": errs,
        })
    }

    return c.JSON(http.StatusCreated, req)
}
```

---

## Topic 10: Connecting to PostgreSQL

### What is PostgreSQL?

PostgreSQL is an open-source, production-grade relational database. In Go, you connect to it using the standard `database/sql` package along with a driver.

### Install the lib/pq driver

```bash
go get github.com/lib/pq
```

### Connection String Format

```
postgresql://username:password@host:port/dbname?sslmode=disable

Examples:
postgresql://postgres:secret@localhost:5432/myapp?sslmode=disable
postgresql://admin:pass123@db.example.com:5432/production?sslmode=require
```

### Connecting to PostgreSQL

```go
package main

import (
    "database/sql"
    "fmt"
    "log"

    _ "github.com/lib/pq"   // blank import — registers the driver
)

func main() {
    // Connection string
    dsn := "postgresql://postgres:secret@localhost:5432/myapp?sslmode=disable"

    // Open database connection (does NOT actually connect yet)
    db, err := sql.Open("postgres", dsn)
    if err != nil {
        log.Fatal("Failed to create DB instance:", err)
    }
    defer db.Close()

    // Ping to verify the connection works
    if err := db.Ping(); err != nil {
        log.Fatal("Failed to connect to database:", err)
    }

    fmt.Println("✅ Connected to PostgreSQL successfully!")
}
```

### Connection Pool Configuration

```go
// sql.Open creates a connection POOL — not a single connection
// Configure the pool for production use

db, err := sql.Open("postgres", dsn)
if err != nil {
    log.Fatal(err)
}

// Maximum open connections at once
db.SetMaxOpenConns(25)

// Maximum idle connections kept in pool
db.SetMaxIdleConns(10)

// Maximum time a connection can be reused
db.SetConnMaxLifetime(5 * time.Minute)

// Maximum time a connection can be idle
db.SetConnMaxIdleTime(2 * time.Minute)
```

### Environment Variables for DB Config

```go
import "os"

// Never hardcode credentials — use environment variables
func connectDB() (*sql.DB, error) {
    dsn := fmt.Sprintf(
        "postgresql://%s:%s@%s:%s/%s?sslmode=%s",
        os.Getenv("DB_USER"),
        os.Getenv("DB_PASSWORD"),
        os.Getenv("DB_HOST"),
        os.Getenv("DB_PORT"),
        os.Getenv("DB_NAME"),
        os.Getenv("DB_SSLMODE"),
    )

    db, err := sql.Open("postgres", dsn)
    if err != nil {
        return nil, fmt.Errorf("sql.Open: %w", err)
    }

    if err := db.Ping(); err != nil {
        return nil, fmt.Errorf("db.Ping: %w", err)
    }

    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(10)
    db.SetConnMaxLifetime(5 * time.Minute)

    return db, nil
}
```

### .env File Pattern

```bash
# .env file (never commit to git!)
DB_USER=postgres
DB_PASSWORD=secret123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_SSLMODE=disable
```

```go
// Load .env file
go get github.com/joho/godotenv

// In main.go
import "github.com/joho/godotenv"

func main() {
    godotenv.Load()   // loads .env into os.Getenv

    db, err := connectDB()
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()
}
```

### Passing DB to Handlers — Dependency Injection

```go
// Handler struct holds DB reference
type UserHandler struct {
    db *sql.DB
}

func NewUserHandler(db *sql.DB) *UserHandler {
    return &UserHandler{db: db}
}

func (h *UserHandler) GetUsers(c echo.Context) error {
    rows, err := h.db.Query("SELECT id, name, email FROM users")
    // ...
}

// In main.go
func main() {
    e := echo.New()
    db, _ := connectDB()

    userHandler := NewUserHandler(db)
    e.GET("/users", userHandler.GetUsers)
    e.POST("/users", userHandler.CreateUser)

    e.Logger.Fatal(e.Start(":8080"))
}
```

---

## Topic 11: database/sql & lib/pq Driver

### How database/sql Works

```
Your Code
    ↓
database/sql   ← standard interface (same for all databases)
    ↓
lib/pq driver  ← PostgreSQL-specific implementation
    ↓
PostgreSQL
```

The `database/sql` package provides a common interface. The `lib/pq` driver translates that interface into PostgreSQL wire protocol calls.

### Query vs Exec vs QueryRow

```go
// ── db.Query() ────────────────────────────────────────────────
// Use for SELECT that returns MULTIPLE rows
rows, err := db.Query("SELECT id, name, email FROM users")
if err != nil {
    return err
}
defer rows.Close()   // ALWAYS defer close!

var users []User
for rows.Next() {
    var u User
    err := rows.Scan(&u.ID, &u.Name, &u.Email)
    if err != nil {
        return err
    }
    users = append(users, u)
}
// Check for errors from iteration
if err := rows.Err(); err != nil {
    return err
}

// ── db.QueryRow() ─────────────────────────────────────────────
// Use for SELECT that returns EXACTLY ONE row
var u User
err := db.QueryRow(
    "SELECT id, name, email FROM users WHERE id = $1", id,
).Scan(&u.ID, &u.Name, &u.Email)

if err == sql.ErrNoRows {
    return c.JSON(http.StatusNotFound, map[string]string{
        "error": "user not found",
    })
}
if err != nil {
    return err
}

// ── db.Exec() ─────────────────────────────────────────────────
// Use for INSERT, UPDATE, DELETE — no rows returned
result, err := db.Exec(
    "INSERT INTO users (name, email) VALUES ($1, $2)",
    "Rahul", "rahul@example.com",
)
if err != nil {
    return err
}

// Get number of affected rows
rowsAffected, _ := result.RowsAffected()
fmt.Println("Rows affected:", rowsAffected)
```

### PostgreSQL Placeholders

```go
// PostgreSQL uses $1, $2, $3... (NOT ?)
// NEVER use string formatting for SQL — SQL injection risk!

// ❌ WRONG — SQL injection vulnerability!
query := fmt.Sprintf("SELECT * FROM users WHERE id = %d", id)

// ✅ CORRECT — use parameterized queries
rows, err := db.Query("SELECT * FROM users WHERE id = $1", id)

// Multiple parameters
rows, err := db.Query(
    "SELECT * FROM users WHERE name = $1 AND age > $2",
    name, minAge,
)
```

### Full CRUD with database/sql

```go
type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

// ── CREATE ────────────────────────────────────────────────────
func (h *UserHandler) CreateUser(c echo.Context) error {
    var req struct {
        Name  string `json:"name"`
        Email string `json:"email"`
    }
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid body"})
    }

    var user User
    err := h.db.QueryRow(
        `INSERT INTO users (name, email)
         VALUES ($1, $2)
         RETURNING id, name, email, created_at`,
        req.Name, req.Email,
    ).Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt)

    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not create user",
        })
    }

    return c.JSON(http.StatusCreated, user)
}

// ── READ ALL ──────────────────────────────────────────────────
func (h *UserHandler) GetUsers(c echo.Context) error {
    rows, err := h.db.Query(
        "SELECT id, name, email, created_at FROM users ORDER BY id",
    )
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not fetch users",
        })
    }
    defer rows.Close()

    users := []User{}
    for rows.Next() {
        var u User
        if err := rows.Scan(&u.ID, &u.Name, &u.Email, &u.CreatedAt); err != nil {
            return c.JSON(http.StatusInternalServerError, map[string]string{
                "error": "could not scan user",
            })
        }
        users = append(users, u)
    }

    return c.JSON(http.StatusOK, users)
}

// ── READ ONE ──────────────────────────────────────────────────
func (h *UserHandler) GetUserByID(c echo.Context) error {
    id, err := strconv.Atoi(c.Param("id"))
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
    }

    var user User
    err = h.db.QueryRow(
        "SELECT id, name, email, created_at FROM users WHERE id = $1", id,
    ).Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt)

    if err == sql.ErrNoRows {
        return c.JSON(http.StatusNotFound, map[string]string{"error": "user not found"})
    }
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{"error": "db error"})
    }

    return c.JSON(http.StatusOK, user)
}

// ── UPDATE ────────────────────────────────────────────────────
func (h *UserHandler) UpdateUser(c echo.Context) error {
    id, err := strconv.Atoi(c.Param("id"))
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
    }

    var req struct {
        Name  string `json:"name"`
        Email string `json:"email"`
    }
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid body"})
    }

    var user User
    err = h.db.QueryRow(
        `UPDATE users SET name=$1, email=$2
         WHERE id=$3
         RETURNING id, name, email, created_at`,
        req.Name, req.Email, id,
    ).Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt)

    if err == sql.ErrNoRows {
        return c.JSON(http.StatusNotFound, map[string]string{"error": "user not found"})
    }
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{"error": "db error"})
    }

    return c.JSON(http.StatusOK, user)
}

// ── DELETE ────────────────────────────────────────────────────
func (h *UserHandler) DeleteUser(c echo.Context) error {
    id, err := strconv.Atoi(c.Param("id"))
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
    }

    result, err := h.db.Exec("DELETE FROM users WHERE id = $1", id)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{"error": "db error"})
    }

    rowsAffected, _ := result.RowsAffected()
    if rowsAffected == 0 {
        return c.JSON(http.StatusNotFound, map[string]string{"error": "user not found"})
    }

    return c.NoContent(http.StatusNoContent)
}
```

### Transactions

```go
// Use transactions when multiple DB operations must all succeed or all fail
func (h *UserHandler) TransferBalance(c echo.Context) error {
    // ── Start transaction ─────────────────────────────────────
    tx, err := h.db.Begin()
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not start transaction",
        })
    }
    // If anything goes wrong, rollback ALL changes
    defer tx.Rollback()

    // ── Operation 1: deduct from sender ───────────────────────
    _, err = tx.Exec(
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
        100, senderID,
    )
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "deduction failed",
        })
    }

    // ── Operation 2: add to receiver ──────────────────────────
    _, err = tx.Exec(
        "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
        100, receiverID,
    )
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "credit failed",
        })
    }

    // ── Commit — makes all changes permanent ──────────────────
    if err := tx.Commit(); err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "commit failed",
        })
    }

    return c.JSON(http.StatusOK, map[string]string{"message": "transfer complete"})
}
```

### Handling NULL Values

```go
import "database/sql"

type User struct {
    ID    int
    Name  string
    Email string
    Phone sql.NullString  // nullable string
    Age   sql.NullInt64   // nullable int
}

rows, _ := db.Query("SELECT id, name, email, phone, age FROM users")
for rows.Next() {
    var u User
    rows.Scan(&u.ID, &u.Name, &u.Email, &u.Phone, &u.Age)

    if u.Phone.Valid {
        fmt.Println("Phone:", u.Phone.String)
    } else {
        fmt.Println("Phone: NULL")
    }
}
```

### Complete Project Setup

```go
// ── main.go ───────────────────────────────────────────────────
package main

import (
    "database/sql"
    "log"
    "os"

    "github.com/joho/godotenv"
    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
    _ "github.com/lib/pq"
)

func main() {
    // Load environment variables
    godotenv.Load()

    // Connect to DB
    dsn := fmt.Sprintf(
        "postgresql://%s:%s@%s:%s/%s?sslmode=%s",
        os.Getenv("DB_USER"), os.Getenv("DB_PASSWORD"),
        os.Getenv("DB_HOST"), os.Getenv("DB_PORT"),
        os.Getenv("DB_NAME"), os.Getenv("DB_SSLMODE"),
    )

    db, err := sql.Open("postgres", dsn)
    if err != nil {
        log.Fatal("DB open error:", err)
    }
    defer db.Close()

    if err := db.Ping(); err != nil {
        log.Fatal("DB ping error:", err)
    }
    log.Println("Database connected!")

    // Echo setup
    e := echo.New()
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())

    // Inject DB into handlers
    h := NewUserHandler(db)

    // Routes
    api := e.Group("/api/v1")
    api.GET("/users",        h.GetUsers)
    api.POST("/users",       h.CreateUser)
    api.GET("/users/:id",    h.GetUserByID)
    api.PUT("/users/:id",    h.UpdateUser)
    api.DELETE("/users/:id", h.DeleteUser)

    log.Println("Server starting on :8080")
    e.Logger.Fatal(e.Start(":8080"))
}
```

### Create PostgreSQL Table

```sql
-- Run this SQL to create the users table
CREATE TABLE users (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Interview Questions

### Topic 7 & 8: Request Handling

**Q: What is the difference between path params and query params?**
> Path params are part of the URL path — `/users/:id` — they identify a specific resource. Query params come after `?` — `/users?page=2&sort=name` — they filter, sort, or paginate. Path params are required by the route definition; query params are usually optional.

**Q: How does c.Bind() work in Echo?**
> `c.Bind(&struct)` reads the `Content-Type` header and decodes accordingly. For `application/json` it decodes JSON body. For `application/x-www-form-urlencoded` it reads form data. For URL params it reads path params. It always returns an error you must check.

**Q: What is the correct order for handling a request?**
> Bind input → Validate input → Call business logic → Return response. Never skip validation. Always check binding errors before using the data. Return early on any error.

**Q: How do you return a consistent API response in Go?**
> Define a standard response struct like `APIResponse{Success bool; Data interface{}; Error string}` and use it for all responses. This makes the API predictable for the frontend.

---

### Topic 9: Validation

**Q: Why do you need input validation even if the database has constraints?**
> Database constraints are the last line of defense. Validating early gives better error messages, saves a DB round-trip for invalid data, and prevents crashes from unexpected input. Return human-readable errors before the data ever reaches the DB.

**Q: What is the difference between 400 and 422 status codes?**
> 400 Bad Request — the request is malformed (invalid JSON, wrong Content-Type, missing body). 422 Unprocessable Entity — the request format is correct but the content fails validation (name too long, email invalid, age negative).

**Q: What does the `omitempty` validation tag do?**
> `omitempty` skips all other validation tags if the field is empty/zero. Used for optional fields that should still be validated if provided. Example: `validate:"omitempty,email"` — only validates as email format if a value is given.

---

### Topic 10 & 11: PostgreSQL & database/sql

**Q: What is the difference between sql.Open and db.Ping?**
> `sql.Open` does NOT actually connect to the database — it just creates the connection pool object and validates the driver. `db.Ping()` actually attempts a connection and returns an error if the DB is unreachable. Always call Ping after Open to verify connectivity.

**Q: What is a connection pool and why is it important?**
> A pool maintains multiple reusable connections instead of creating a new one for every request. Creating a DB connection is expensive (TCP handshake, auth). With a pool, connections are borrowed and returned. `SetMaxOpenConns` limits the total, `SetMaxIdleConns` keeps warm connections ready.

**Q: What is the difference between db.Query, db.QueryRow, and db.Exec?**
> `db.Query` — for SELECT returning multiple rows. Returns `*sql.Rows`, must scan each row. `db.QueryRow` — for SELECT returning exactly one row. Returns `*sql.Row`, scan directly. `db.Exec` — for INSERT, UPDATE, DELETE. No rows returned, gives `RowsAffected`.

**Q: Why should you never use string formatting to build SQL queries?**
> SQL injection. If user input is directly inserted into the query string, an attacker can manipulate the query. Always use parameterized queries with `$1, $2` placeholders. The driver safely escapes the values.

**Q: What is sql.ErrNoRows and when do you get it?**
> It's the error returned by `db.QueryRow().Scan()` when no row matches the WHERE clause. You must check for it explicitly: `if err == sql.ErrNoRows { return 404 }`. Without this check, you'd return 500 instead of 404 for "not found" cases.

**Q: What is a database transaction and when do you use it?**
> A transaction groups multiple SQL operations so they either ALL succeed or ALL fail — atomicity. Use when multiple operations depend on each other (e.g., bank transfer: deduct from one account, add to another). Use `db.Begin()`, execute operations, then `tx.Commit()` or `tx.Rollback()`.

**Q: Why do you blank import lib/pq with `_ "github.com/lib/pq"`?**
> The blank import runs the package's `init()` function which registers the `"postgres"` driver with `database/sql`. You don't use any exported names from `lib/pq` directly — `database/sql` uses the registered driver internally when you call `sql.Open("postgres", dsn)`.

---

## Quick Reference Cheatsheet

```go
// ── READING INPUT ───────────────────────────────────────────────
c.Param("id")                    // path param  /users/:id
c.QueryParam("page")             // query param ?page=2
c.Request().Header.Get("Authorization") // header
c.Bind(&req)                     // decode JSON body

// ── VALIDATION SETUP ───────────────────────────────────────────
type CustomValidator struct{ v *validator.Validate }
func (cv *CustomValidator) Validate(i interface{}) error {
    return cv.v.Struct(i)
}
e.Validator = &CustomValidator{v: validator.New()}

// ── VALIDATION TAGS ────────────────────────────────────────────
type Req struct {
    Name  string `validate:"required,min=2,max=50"`
    Email string `validate:"required,email"`
    Age   int    `validate:"required,min=0,max=120"`
    Role  string `validate:"required,oneof=admin user"`
    Phone string `validate:"omitempty,e164"`
}

// ── POSTGRESQL CONNECTION ──────────────────────────────────────
import _ "github.com/lib/pq"    // blank import — registers driver

dsn := "postgresql://user:pass@localhost:5432/dbname?sslmode=disable"
db, err := sql.Open("postgres", dsn)  // creates pool, doesn't connect
db.Ping()                              // actually connects

db.SetMaxOpenConns(25)
db.SetMaxIdleConns(10)
db.SetConnMaxLifetime(5 * time.Minute)

// ── DB OPERATIONS ──────────────────────────────────────────────
// SELECT many rows
rows, err := db.Query("SELECT id, name FROM users WHERE age > $1", 18)
defer rows.Close()
for rows.Next() { rows.Scan(&u.ID, &u.Name) }
rows.Err()

// SELECT one row
err := db.QueryRow("SELECT id, name FROM users WHERE id=$1", id).
    Scan(&u.ID, &u.Name)
if err == sql.ErrNoRows { /* 404 */ }

// INSERT with RETURNING
db.QueryRow("INSERT INTO users(name) VALUES($1) RETURNING id", name).
    Scan(&u.ID)

// UPDATE / DELETE
result, _ := db.Exec("DELETE FROM users WHERE id=$1", id)
result.RowsAffected()   // check if row existed

// ── TRANSACTIONS ───────────────────────────────────────────────
tx, _ := db.Begin()
defer tx.Rollback()     // no-op if committed
tx.Exec("UPDATE accounts SET bal=bal-$1 WHERE id=$2", 100, from)
tx.Exec("UPDATE accounts SET bal=bal+$1 WHERE id=$2", 100, to)
tx.Commit()

// ── NEVER DO THIS (SQL injection) ─────────────────────────────
// query := fmt.Sprintf("SELECT * FROM users WHERE id=%d", id) ❌

// ── STATUS CODES ──────────────────────────────────────────────
// 200 OK, 201 Created, 204 No Content
// 400 Bad Request (malformed), 401 Unauthorized
// 403 Forbidden, 404 Not Found, 422 Validation Failed
// 500 Internal Server Error
```

---

## Resources

- [go-playground/validator Docs](https://github.com/go-playground/validator)
- [lib/pq Driver Docs](https://github.com/lib/pq)
- [database/sql Tutorial](https://go.dev/doc/database/querying)
- [Echo — Request Handling](https://echo.labstack.com/docs/request)
- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)

---

*Phase 2 — Days 8–14 | Topics 7–11 Covered ✅*
*Phase 2 Fully Complete — All 11 Topics Done! 🎉*