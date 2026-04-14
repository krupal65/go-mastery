# 🐹 Go Language — Phase 2 Study Notes (Days 8–14)

> Complete notes for the **First 6 Topics of Phase 2:**
> - **Topic 1: Intro to REST APIs & HTTP in Go**
> - **Topic 2: net/http Basics**
> - **Topic 3: First API Endpoint Without Frameworks**
> - **Topic 4: Using Echo Framework**
> - **Topic 5: Setting up Echo**
> - **Topic 6: Routing, Middlewares, and JSON Responses**

---

## 📚 Table of Contents

- [Topic 1: Intro to REST APIs & HTTP in Go](#topic-1-intro-to-rest-apis--http-in-go)
- [Topic 2: net/http Basics](#topic-2-nethttp-basics)
- [Topic 3: First API Endpoint Without Frameworks](#topic-3-first-api-endpoint-without-frameworks)
- [Topic 4: Using Echo Framework](#topic-4-using-echo-framework)
- [Topic 5: Setting up Echo](#topic-5-setting-up-echo)
- [Topic 6: Routing, Middlewares, and JSON Responses](#topic-6-routing-middlewares-and-json-responses)
- [Interview Questions](#interview-questions)
- [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Topic 1: Intro to REST APIs & HTTP in Go

### What is REST?

**REST** (Representational State Transfer) is an architectural style for designing web APIs. A REST API uses HTTP methods to perform operations on resources.

### HTTP Methods

| Method | Purpose | Example |
|---|---|---|
| `GET` | Read / fetch data | `GET /users` — get all users |
| `POST` | Create new resource | `POST /users` — create a user |
| `PUT` | Replace entire resource | `PUT /users/1` — replace user |
| `PATCH` | Partially update resource | `PATCH /users/1` — update fields |
| `DELETE` | Remove resource | `DELETE /users/1` — delete user |

### HTTP Status Codes

| Code | Meaning | Use When |
|---|---|---|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Invalid input from client |
| `401` | Unauthorized | Not logged in |
| `403` | Forbidden | Logged in but no permission |
| `404` | Not Found | Resource doesn't exist |
| `422` | Unprocessable Entity | Validation failed |
| `500` | Internal Server Error | Server-side bug |

### REST URL Conventions

```
GET    /users           → list all users
GET    /users/1         → get user with id=1
POST   /users           → create new user
PUT    /users/1         → replace user with id=1
PATCH  /users/1         → partial update user with id=1
DELETE /users/1         → delete user with id=1

GET    /users/1/posts   → all posts by user 1
GET    /users/1/posts/5 → post 5 of user 1
```

### HTTP Request Structure

```
POST /users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOi...

{
    "name": "Rahul",
    "email": "rahul@example.com",
    "age": 25
}
```

### HTTP Response Structure

```
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": 1,
    "name": "Rahul",
    "email": "rahul@example.com",
    "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Topic 2: net/http Basics

Go's built-in `net/http` package provides everything needed to build HTTP servers and clients without any external library.

### Simple HTTP Server

```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    // Register handler for route "/"
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintln(w, "Hello, World!")
    })

    // Start server on port 8080
    fmt.Println("Server running on http://localhost:8080")
    http.ListenAndServe(":8080", nil)
}
```

### http.ResponseWriter

`ResponseWriter` is used to write the HTTP response back to the client:

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // Set response headers
    w.Header().Set("Content-Type", "application/json")
    w.Header().Set("X-Custom-Header", "myvalue")

    // Set status code — MUST be called BEFORE writing body
    w.WriteHeader(http.StatusCreated)   // 201

    // Write response body
    fmt.Fprintln(w, `{"message": "created"}`)
}
```

> ⚠️ Always call `w.WriteHeader()` BEFORE `w.Write()` or `fmt.Fprintln(w, ...)`. Once you start writing the body, headers are locked.

### http.Request

`Request` contains everything about the incoming HTTP request:

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // HTTP method
    fmt.Println(r.Method)          // "GET", "POST", etc.

    // Request URL and path
    fmt.Println(r.URL.Path)        // "/users/1"
    fmt.Println(r.URL.RawQuery)    // "page=2&limit=10"

    // Query parameters
    page  := r.URL.Query().Get("page")    // "2"
    limit := r.URL.Query().Get("limit")   // "10"

    // Request headers
    token := r.Header.Get("Authorization")

    // Read request body (for POST/PUT)
    body, err := io.ReadAll(r.Body)
    defer r.Body.Close()

    // Remote address of client
    fmt.Println(r.RemoteAddr)   // "192.168.1.1:54321"
}
```

### Sending JSON Response

```go
import (
    "encoding/json"
    "net/http"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

func getUserHandler(w http.ResponseWriter, r *http.Request) {
    user := User{ID: 1, Name: "Rahul", Email: "rahul@example.com"}

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)

    // Encode struct as JSON and write to response
    json.NewEncoder(w).Encode(user)
}
```

### Reading JSON Request Body

```go
func createUserHandler(w http.ResponseWriter, r *http.Request) {
    // Only allow POST
    if r.Method != http.MethodPost {
        w.WriteHeader(http.StatusMethodNotAllowed)
        return
    }

    var user User
    err := json.NewDecoder(r.Body).Decode(&user)
    if err != nil {
        w.WriteHeader(http.StatusBadRequest)
        json.NewEncoder(w).Encode(map[string]string{
            "error": "invalid JSON body",
        })
        return
    }

    // Process user...
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(user)
}
```

### http.ServeMux — Custom Router

```go
func main() {
    mux := http.NewServeMux()

    // Register routes
    mux.HandleFunc("/", homeHandler)
    mux.HandleFunc("/users", usersHandler)
    mux.HandleFunc("/users/", userByIDHandler)

    fmt.Println("Server on :8080")
    http.ListenAndServe(":8080", mux)
}

func usersHandler(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case http.MethodGet:
        // handle GET /users
    case http.MethodPost:
        // handle POST /users
    default:
        w.WriteHeader(http.StatusMethodNotAllowed)
    }
}
```

### HTTP Client

```go
// GET request
resp, err := http.Get("https://api.example.com/users")
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()

body, _ := io.ReadAll(resp.Body)
fmt.Println(string(body))

// POST request with JSON body
payload := bytes.NewBufferString(`{"name":"Rahul"}`)
resp, err := http.Post(
    "https://api.example.com/users",
    "application/json",
    payload,
)
defer resp.Body.Close()

// Custom request with headers
req, _ := http.NewRequest("DELETE", "https://api.example.com/users/1", nil)
req.Header.Set("Authorization", "Bearer mytoken")

client := &http.Client{}
resp, err = client.Do(req)
```

---

## Topic 3: First API Endpoint Without Frameworks

Building a complete REST API using only `net/http` — no external packages.

### Project Structure

```
myapi/
├── go.mod
└── main.go
```

### Complete Users CRUD API

```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "strconv"
    "strings"
)

// ── Models ──────────────────────────────────────────────────────
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

// ── In-memory store ─────────────────────────────────────────────
var (
    users  = []User{}
    nextID = 1
)

// ── Helpers ─────────────────────────────────────────────────────
func writeJSON(w http.ResponseWriter, status int, data interface{}) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, status int, msg string) {
    writeJSON(w, status, map[string]string{"error": msg})
}

// ── Handlers ────────────────────────────────────────────────────

// GET /users
func getUsers(w http.ResponseWriter, r *http.Request) {
    writeJSON(w, http.StatusOK, users)
}

// POST /users
func createUser(w http.ResponseWriter, r *http.Request) {
    var u User
    if err := json.NewDecoder(r.Body).Decode(&u); err != nil {
        writeError(w, http.StatusBadRequest, "invalid JSON")
        return
    }
    if u.Name == "" {
        writeError(w, http.StatusBadRequest, "name is required")
        return
    }
    u.ID = nextID
    nextID++
    users = append(users, u)
    writeJSON(w, http.StatusCreated, u)
}

// GET /users/{id}
func getUserByID(w http.ResponseWriter, r *http.Request) {
    // Extract ID from path /users/1
    parts := strings.Split(r.URL.Path, "/")
    id, err := strconv.Atoi(parts[len(parts)-1])
    if err != nil {
        writeError(w, http.StatusBadRequest, "invalid id")
        return
    }
    for _, u := range users {
        if u.ID == id {
            writeJSON(w, http.StatusOK, u)
            return
        }
    }
    writeError(w, http.StatusNotFound, "user not found")
}

// ── Router ──────────────────────────────────────────────────────
func usersRouter(w http.ResponseWriter, r *http.Request) {
    // /users  or /users/
    if r.URL.Path == "/users" || r.URL.Path == "/users/" {
        switch r.Method {
        case http.MethodGet:
            getUsers(w, r)
        case http.MethodPost:
            createUser(w, r)
        default:
            writeError(w, http.StatusMethodNotAllowed, "method not allowed")
        }
        return
    }
    // /users/{id}
    switch r.Method {
    case http.MethodGet:
        getUserByID(w, r)
    default:
        writeError(w, http.StatusMethodNotAllowed, "method not allowed")
    }
}

// ── Main ────────────────────────────────────────────────────────
func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/users", usersRouter)
    mux.HandleFunc("/users/", usersRouter)

    fmt.Println("🚀 Server running on http://localhost:8080")
    http.ListenAndServe(":8080", mux)
}
```

### Testing with curl

```bash
# GET all users
curl http://localhost:8080/users

# POST create user
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Rahul","email":"rahul@example.com"}'

# GET user by ID
curl http://localhost:8080/users/1
```

---

## Topic 4: Using Echo Framework

**Echo** is a fast, minimalist web framework for Go. It provides routing, middleware, request binding, and response helpers that make building APIs much cleaner than raw `net/http`.

### Why Echo over net/http?

| Feature | net/http | Echo |
|---|---|---|
| Path parameters | Manual parsing | `c.Param("id")` |
| Query parameters | `r.URL.Query().Get("page")` | `c.QueryParam("page")` |
| JSON binding | `json.NewDecoder(r.Body).Decode()` | `c.Bind(&user)` |
| JSON response | Manual headers + encode | `c.JSON(200, data)` |
| Middleware | Manual wrapping | `e.Use(middleware)` |
| Route groups | Manual | `g := e.Group("/api/v1")` |
| Path params | Manual string split | Built-in `/users/:id` |

### Installation

```bash
go get github.com/labstack/echo/v4
go get github.com/labstack/echo/v4/middleware
```

### Echo Context

The `echo.Context` is the heart of Echo — it wraps `http.Request` and `http.ResponseWriter` and provides helper methods:

```go
import "github.com/labstack/echo/v4"

func handler(c echo.Context) error {
    // Path parameter
    id := c.Param("id")

    // Query parameter
    page := c.QueryParam("page")

    // Request header
    token := c.Request().Header.Get("Authorization")

    // Send JSON response
    return c.JSON(http.StatusOK, map[string]string{
        "id": id,
    })

    // Send string response
    return c.String(http.StatusOK, "Hello!")

    // Send with status only
    return c.NoContent(http.StatusNoContent)
}
```

---

## Topic 5: Setting up Echo

### Minimal Echo Server

```go
package main

import (
    "net/http"
    "github.com/labstack/echo/v4"
)

func main() {
    // Create new Echo instance
    e := echo.New()

    // Define a route
    e.GET("/", func(c echo.Context) error {
        return c.String(http.StatusOK, "Hello, Echo!")
    })

    // Start server
    e.Logger.Fatal(e.Start(":8080"))
}
```

### Echo with Built-in Middleware

```go
package main

import (
    "net/http"
    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
)

func main() {
    e := echo.New()

    // ── Global Middleware ──────────────────────────────────────
    e.Use(middleware.Logger())    // logs every request
    e.Use(middleware.Recover())   // recovers from panics
    e.Use(middleware.CORS())      // enables CORS

    // ── Routes ────────────────────────────────────────────────
    e.GET("/", homeHandler)
    e.GET("/health", healthHandler)

    // Start server
    e.Logger.Fatal(e.Start(":8080"))
}

func homeHandler(c echo.Context) error {
    return c.JSON(http.StatusOK, map[string]string{
        "message": "Welcome to my API",
        "version": "1.0.0",
    })
}

func healthHandler(c echo.Context) error {
    return c.JSON(http.StatusOK, map[string]string{
        "status": "healthy",
    })
}
```

### Project Structure for Echo API

```
myapi/
├── go.mod
├── go.sum
├── main.go
├── handlers/
│   ├── user.go
│   └── product.go
├── models/
│   └── user.go
└── middleware/
    └── auth.go
```

### Binding Request Body

```go
type CreateUserRequest struct {
    Name  string `json:"name"  validate:"required"`
    Email string `json:"email" validate:"required,email"`
    Age   int    `json:"age"   validate:"min=0,max=120"`
}

func createUser(c echo.Context) error {
    var req CreateUserRequest

    // Bind JSON body to struct
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid request body",
        })
    }

    // Validate (requires validator setup)
    if err := c.Validate(&req); err != nil {
        return c.JSON(http.StatusUnprocessableEntity, map[string]string{
            "error": err.Error(),
        })
    }

    // Create user in DB...
    return c.JSON(http.StatusCreated, req)
}
```

---

## Topic 6: Routing, Middlewares, and JSON Responses

### Echo Routing — All Features

```go
e := echo.New()

// ── HTTP Methods ───────────────────────────────────────────────
e.GET("/users",        getUsers)
e.POST("/users",       createUser)
e.PUT("/users/:id",    updateUser)
e.PATCH("/users/:id",  patchUser)
e.DELETE("/users/:id", deleteUser)

// ── Path Parameters ────────────────────────────────────────────
e.GET("/users/:id", func(c echo.Context) error {
    id := c.Param("id")   // returns string
    return c.JSON(200, map[string]string{"id": id})
})

// Multiple path parameters
e.GET("/users/:userID/posts/:postID", func(c echo.Context) error {
    userID := c.Param("userID")
    postID := c.Param("postID")
    return c.JSON(200, map[string]string{
        "userID": userID,
        "postID": postID,
    })
})

// ── Query Parameters ───────────────────────────────────────────
// GET /users?page=2&limit=10&sort=name
e.GET("/users", func(c echo.Context) error {
    page  := c.QueryParam("page")   // "2"
    limit := c.QueryParam("limit")  // "10"
    sort  := c.QueryParam("sort")   // "name"

    // With default value
    if page == "" { page = "1" }

    return c.JSON(200, map[string]string{
        "page": page, "limit": limit, "sort": sort,
    })
})

// ── Route Groups ───────────────────────────────────────────────
v1 := e.Group("/api/v1")
v1.GET("/users",    getUsers)
v1.POST("/users",   createUser)
v1.GET("/products", getProducts)

// Nested group with middleware
admin := e.Group("/admin")
admin.Use(authMiddleware)   // only admin routes need auth
admin.GET("/stats",  getStats)
admin.DELETE("/users/:id", adminDeleteUser)
```

### JSON Responses — All Patterns

```go
// ── Success Responses ──────────────────────────────────────────

// 200 OK with data
return c.JSON(http.StatusOK, user)

// 201 Created
return c.JSON(http.StatusCreated, newUser)

// 204 No Content (for DELETE)
return c.NoContent(http.StatusNoContent)

// ── Response with wrapper ─────────────────────────────────────
type APIResponse struct {
    Success bool        `json:"success"`
    Message string      `json:"message,omitempty"`
    Data    interface{} `json:"data,omitempty"`
    Error   string      `json:"error,omitempty"`
}

// Success
return c.JSON(http.StatusOK, APIResponse{
    Success: true,
    Data:    users,
})

// Error
return c.JSON(http.StatusBadRequest, APIResponse{
    Success: false,
    Error:   "name is required",
})

// ── JSON struct tags ──────────────────────────────────────────
type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    Password  string    `json:"-"`             // never include in JSON
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at,omitempty"` // omit if zero
}
```

### Middlewares — Built-in and Custom

```go
// ── Built-in Middleware ────────────────────────────────────────
e.Use(middleware.Logger())       // request logging
e.Use(middleware.Recover())      // panic recovery
e.Use(middleware.CORS())         // cross-origin requests

// CORS with config
e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
    AllowOrigins: []string{"https://myapp.com", "http://localhost:3000"},
    AllowMethods: []string{http.MethodGet, http.MethodPost, http.MethodDelete},
    AllowHeaders: []string{"Content-Type", "Authorization"},
}))

// Rate limiting
e.Use(middleware.RateLimiter(middleware.NewRateLimiterMemoryStore(20)))

// JWT Auth
e.Use(middleware.JWTWithConfig(middleware.JWTConfig{
    SigningKey: []byte("my-secret-key"),
}))

// ── Custom Middleware ──────────────────────────────────────────
// A middleware is a function that wraps a handler
func requestIDMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        // Code BEFORE handler runs
        requestID := fmt.Sprintf("%d", time.Now().UnixNano())
        c.Request().Header.Set("X-Request-ID", requestID)
        c.Response().Header().Set("X-Request-ID", requestID)

        // Call the next handler
        err := next(c)

        // Code AFTER handler runs
        fmt.Printf("Request %s completed\n", requestID)

        return err
    }
}

// Register custom middleware
e.Use(requestIDMiddleware)

// ── Route-level Middleware ─────────────────────────────────────
// Apply middleware to specific routes only
e.GET("/protected", protectedHandler, authMiddleware)

// Apply to group
api := e.Group("/api")
api.Use(authMiddleware)
api.GET("/profile", getProfile)

// ── Auth Middleware Example ────────────────────────────────────
func authMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        token := c.Request().Header.Get("Authorization")
        if token == "" {
            return c.JSON(http.StatusUnauthorized, map[string]string{
                "error": "authorization header required",
            })
        }
        if token != "Bearer valid-token" {
            return c.JSON(http.StatusForbidden, map[string]string{
                "error": "invalid token",
            })
        }
        return next(c)   // token valid — proceed to handler
    }
}
```

### Complete Echo CRUD API Example

```go
package main

import (
    "net/http"
    "strconv"

    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

var users = []User{}
var nextID = 1

func main() {
    e := echo.New()
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())

    // Routes
    e.GET("/users",        getUsers)
    e.POST("/users",       createUser)
    e.GET("/users/:id",    getUserByID)
    e.PUT("/users/:id",    updateUser)
    e.DELETE("/users/:id", deleteUser)

    e.Logger.Fatal(e.Start(":8080"))
}

func getUsers(c echo.Context) error {
    return c.JSON(http.StatusOK, users)
}

func createUser(c echo.Context) error {
    var u User
    if err := c.Bind(&u); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid body",
        })
    }
    if u.Name == "" {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "name is required",
        })
    }
    u.ID = nextID
    nextID++
    users = append(users, u)
    return c.JSON(http.StatusCreated, u)
}

func getUserByID(c echo.Context) error {
    id, err := strconv.Atoi(c.Param("id"))
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid id",
        })
    }
    for _, u := range users {
        if u.ID == id {
            return c.JSON(http.StatusOK, u)
        }
    }
    return c.JSON(http.StatusNotFound, map[string]string{
        "error": "user not found",
    })
}

func updateUser(c echo.Context) error {
    id, err := strconv.Atoi(c.Param("id"))
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
    }
    var updated User
    if err := c.Bind(&updated); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid body"})
    }
    for i, u := range users {
        if u.ID == id {
            updated.ID = id
            users[i] = updated
            return c.JSON(http.StatusOK, updated)
        }
    }
    return c.JSON(http.StatusNotFound, map[string]string{"error": "user not found"})
}

func deleteUser(c echo.Context) error {
    id, err := strconv.Atoi(c.Param("id"))
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
    }
    for i, u := range users {
        if u.ID == id {
            users = append(users[:i], users[i+1:]...)
            return c.NoContent(http.StatusNoContent)
        }
    }
    return c.JSON(http.StatusNotFound, map[string]string{"error": "user not found"})
}
```

---

## Interview Questions

### Topic 1 & 2: REST + net/http

**Q: What is REST and what are the main HTTP methods?**
> REST is an architectural style for APIs using HTTP. Main methods: GET (read), POST (create), PUT (replace), PATCH (partial update), DELETE (remove). Each maps to a CRUD operation.

**Q: What is the difference between PUT and PATCH?**
> PUT replaces the entire resource — you send the full object. PATCH partially updates — you send only the fields you want to change. In practice, many APIs use PUT for both but technically they are different.

**Q: What HTTP status code do you return for a successful POST?**
> 201 Created. For successful GET/PUT/PATCH use 200 OK. For DELETE use 204 No Content (no body). For validation errors use 422 Unprocessable Entity or 400 Bad Request.

**Q: What is http.ResponseWriter and http.Request?**
> `http.ResponseWriter` is the interface for writing the response back to the client — headers, status code, body. `http.Request` contains everything about the incoming request — method, URL, headers, body, query params.

**Q: Why must you call WriteHeader before writing the body?**
> HTTP protocol sends headers before the body. Once you start writing the body, Go flushes the headers with status 200 automatically. Calling `WriteHeader` after the body has started writing is a no-op and logs a warning.

**Q: What is http.ServeMux?**
> The default HTTP request multiplexer (router) in Go's standard library. It matches incoming request URLs to registered handler functions. `http.HandleFunc` registers with the default mux. You can create custom ones with `http.NewServeMux()`.

---

### Topic 3: First API Without Framework

**Q: How do you extract path parameters without a framework?**
> By manually parsing `r.URL.Path`. For example, split `/users/1` by `/` and take the last segment, then convert with `strconv.Atoi`. This is why frameworks like Echo are preferred — they handle this automatically with `:id` patterns.

**Q: How do you read a JSON request body in net/http?**
> Use `json.NewDecoder(r.Body).Decode(&struct)`. Always `defer r.Body.Close()` after reading. Check the error — if decoding fails, return 400 Bad Request.

---

### Topic 4, 5 & 6: Echo Framework

**Q: Why use Echo over the standard net/http?**
> Echo provides: automatic path parameter extraction (`c.Param("id")`), automatic JSON binding (`c.Bind(&req)`), one-line JSON responses (`c.JSON(200, data)`), built-in middleware, route groups, and much cleaner code. Raw net/http requires manual parsing for all of these.

**Q: What is echo.Context?**
> The central object in Echo passed to every handler. It wraps `http.Request` and `http.ResponseWriter` and provides helper methods for params, query params, binding, and responses. You never directly access `ResponseWriter` or `Request` — you use `c.JSON()`, `c.Param()`, etc.

**Q: What is middleware in Echo?**
> A function that wraps a handler and runs code before and/or after it. Signature: `func(next echo.HandlerFunc) echo.HandlerFunc`. Used for logging, authentication, rate limiting, CORS, panic recovery. Applied globally with `e.Use()` or per-route/group.

**Q: What is the difference between global and route-level middleware?**
> Global middleware `e.Use(mw)` applies to every single route in the application. Route-level middleware `e.GET("/path", handler, mw)` applies only to that specific route. Group middleware `g.Use(mw)` applies to all routes in the group.

**Q: What are JSON struct tags and what does json:"-" mean?**
> Struct tags control how a field is serialized to/from JSON. `json:"name"` renames the field. `json:"name,omitempty"` omits the field if it's the zero value. `json:"-"` completely excludes the field from JSON — used for passwords and sensitive data.

**Q: How do you handle errors in Echo handlers?**
> Return the error from the handler: `return c.JSON(400, errResp)` or `return err`. Echo has a centralized error handler. You can set a custom one with `e.HTTPErrorHandler`. Use `echo.NewHTTPError(400, "message")` to create HTTP errors.

---

## Quick Reference Cheatsheet

```go
// ── net/http ────────────────────────────────────────────────────
http.HandleFunc("/path", handler)
http.ListenAndServe(":8080", nil)

func handler(w http.ResponseWriter, r *http.Request) {
    r.Method                        // GET, POST...
    r.URL.Path                      // /users/1
    r.URL.Query().Get("page")       // query param
    r.Header.Get("Authorization")   // header
    io.ReadAll(r.Body)              // read body

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)    // set BEFORE body!
    json.NewEncoder(w).Encode(data) // write JSON
}

// ── Echo Setup ──────────────────────────────────────────────────
e := echo.New()
e.Use(middleware.Logger())
e.Use(middleware.Recover())
e.Use(middleware.CORS())

// ── Echo Routes ─────────────────────────────────────────────────
e.GET("/users",        handler)
e.POST("/users",       handler)
e.PUT("/users/:id",    handler)
e.DELETE("/users/:id", handler)

// Route group
v1 := e.Group("/api/v1")
v1.Use(authMiddleware)
v1.GET("/users", handler)

// ── Echo Context ─────────────────────────────────────────────────
c.Param("id")           // path param  /users/:id
c.QueryParam("page")    // query param ?page=2
c.Bind(&struct)         // decode JSON body

c.JSON(200, data)       // JSON response
c.String(200, "ok")     // text response
c.NoContent(204)        // no body

// ── Custom Middleware ─────────────────────────────────────────────
func myMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        // before handler
        err := next(c)
        // after handler
        return err
    }
}

// ── JSON Struct Tags ──────────────────────────────────────────────
type User struct {
    ID       int    `json:"id"`
    Name     string `json:"name"`
    Password string `json:"-"`              // never in JSON
    Bio      string `json:"bio,omitempty"` // omit if empty
}

// ── Status Codes ──────────────────────────────────────────────────
http.StatusOK                  // 200
http.StatusCreated             // 201
http.StatusNoContent           // 204
http.StatusBadRequest          // 400
http.StatusUnauthorized        // 401
http.StatusForbidden           // 403
http.StatusNotFound            // 404
http.StatusUnprocessableEntity // 422
http.StatusInternalServerError // 500
```

---

## Resources

- [Echo Official Docs](https://echo.labstack.com/)
- [Go net/http Docs](https://pkg.go.dev/net/http)
- [Go by Example — HTTP Server](https://gobyexample.com/http-servers)
- [REST API Design Best Practices](https://restfulapi.net/)

---

*Phase 2 — Days 8–14 | Topics 1–6 Covered ✅*