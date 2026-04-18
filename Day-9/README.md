# 🐹 Go Language — Phase 2 Study Notes

> Complete notes for:
> - **Topic 1: JWT Authentication**
> - **Topic 2: Generating Tokens**
> - **Topic 3: Middleware for Protected Routes**
> - **Topic 4: User Registration & Login**
> - **Topic 5: Password Hashing (bcrypt)**
> - **Topic 6: Login with JWT**
> - **Topic 7: Role-Based Access Control (RBAC)**
> - **Topic 8: Admin/User Roles**
> - **Topic 9: Email Sending**
> - **Topic 10: Using gomail for Sending Emails**

---

## 📚 Table of Contents

- [Topic 1: JWT Authentication](#topic-1-jwt-authentication)
- [Topic 2: Generating Tokens](#topic-2-generating-tokens)
- [Topic 3: Middleware for Protected Routes](#topic-3-middleware-for-protected-routes)
- [Topic 4: User Registration & Login](#topic-4-user-registration--login)
- [Topic 5: Password Hashing (bcrypt)](#topic-5-password-hashing-bcrypt)
- [Topic 6: Login with JWT](#topic-6-login-with-jwt)
- [Topic 7: Role-Based Access Control](#topic-7-role-based-access-control)
- [Topic 8: Admin/User Roles](#topic-8-adminuser-roles)
- [Topic 9: Email Sending](#topic-9-email-sending)
- [Topic 10: Using gomail for Sending Emails](#topic-10-using-gomail-for-sending-emails)
- [Interview Questions](#interview-questions)
- [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Topic 1: JWT Authentication

### What is JWT?

**JWT** (JSON Web Token) is a compact, self-contained token used for authentication. Instead of storing session data on the server, the client holds a signed token that proves their identity.

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InJhaHVsQGV4YW1wbGUuY29tIiwiZXhwIjoxNzA1MzI2MDAwfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

A JWT has **3 parts** separated by dots:

```
HEADER.PAYLOAD.SIGNATURE
```

| Part | Content | Example |
|---|---|---|
| **Header** | Algorithm + token type | `{"alg":"HS256","typ":"JWT"}` |
| **Payload** | Claims (data) | `{"user_id":1,"exp":1705326000}` |
| **Signature** | HMAC of header+payload | Verifies token wasn't tampered |

### How JWT Authentication Works

```
1. User sends POST /login with email + password
2. Server verifies credentials
3. Server creates JWT with user_id, role, expiry — signs with secret
4. Server returns JWT to client
5. Client stores JWT (localStorage or httpOnly cookie)
6. Client sends JWT in every request: Authorization: Bearer <token>
7. Server verifies signature on each request
8. Server extracts user_id from token — no DB lookup needed!
```

### JWT Claims

```go
// Standard claims (registered in JWT spec)
type StandardClaims struct {
    Sub string `json:"sub"`  // Subject — usually user ID
    Iss string `json:"iss"`  // Issuer — your app name
    Aud string `json:"aud"`  // Audience — intended recipient
    Exp int64  `json:"exp"`  // Expiration time (Unix timestamp)
    Iat int64  `json:"iat"`  // Issued at (Unix timestamp)
    Nbf int64  `json:"nbf"`  // Not before
    Jti string `json:"jti"`  // JWT ID (unique ID)
}

// Custom claims — add your own fields
type JWTClaims struct {
    UserID uint   `json:"user_id"`
    Email  string `json:"email"`
    Role   string `json:"role"`
    jwt.RegisteredClaims          // embeds standard claims
}
```

### Install

```bash
go get github.com/golang-jwt/jwt/v5
```

---

## Topic 2: Generating Tokens

### Create JWT Token

```go
package auth

import (
    "time"
    "github.com/golang-jwt/jwt/v5"
)

var jwtSecret = []byte(os.Getenv("JWT_SECRET"))

type JWTClaims struct {
    UserID uint   `json:"user_id"`
    Email  string `json:"email"`
    Role   string `json:"role"`
    jwt.RegisteredClaims
}

// GenerateToken creates a signed JWT for a user
func GenerateToken(userID uint, email, role string) (string, error) {
    claims := JWTClaims{
        UserID: userID,
        Email:  email,
        Role:   role,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            Issuer:    "myapp",
            Subject:   fmt.Sprintf("%d", userID),
        },
    }

    // Create token with HS256 algorithm
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

    // Sign and return the token string
    return token.SignedString(jwtSecret)
}
```

### Parse and Validate JWT Token

```go
// ParseToken verifies signature and extracts claims
func ParseToken(tokenStr string) (*JWTClaims, error) {
    token, err := jwt.ParseWithClaims(
        tokenStr,
        &JWTClaims{},
        func(token *jwt.Token) (interface{}, error) {
            // Verify algorithm is what we expect
            if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
                return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
            }
            return jwtSecret, nil
        },
    )

    if err != nil {
        return nil, fmt.Errorf("invalid token: %w", err)
    }

    // Extract claims
    claims, ok := token.Claims.(*JWTClaims)
    if !ok || !token.Valid {
        return nil, fmt.Errorf("invalid token claims")
    }

    return claims, nil
}
```

### Token with Refresh Token Pattern

```go
// Access token — short lived (15 min to 1 hour)
// Refresh token — long lived (7 to 30 days)

type TokenPair struct {
    AccessToken  string `json:"access_token"`
    RefreshToken string `json:"refresh_token"`
    ExpiresIn    int64  `json:"expires_in"` // seconds
}

func GenerateTokenPair(userID uint, email, role string) (TokenPair, error) {
    // Access token — 1 hour
    accessClaims := JWTClaims{
        UserID: userID, Email: email, Role: role,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(1 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
        },
    }
    accessToken := jwt.NewWithClaims(jwt.SigningMethodHS256, accessClaims)
    accessStr, err := accessToken.SignedString(jwtSecret)
    if err != nil {
        return TokenPair{}, err
    }

    // Refresh token — 7 days (minimal claims)
    refreshClaims := jwt.RegisteredClaims{
        Subject:   fmt.Sprintf("%d", userID),
        ExpiresAt: jwt.NewNumericDate(time.Now().Add(7 * 24 * time.Hour)),
        IssuedAt:  jwt.NewNumericDate(time.Now()),
    }
    refreshToken := jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims)
    refreshStr, err := refreshToken.SignedString(jwtSecret)
    if err != nil {
        return TokenPair{}, err
    }

    return TokenPair{
        AccessToken:  accessStr,
        RefreshToken: refreshStr,
        ExpiresIn:    3600, // 1 hour in seconds
    }, nil
}
```

---

## Topic 3: Middleware for Protected Routes

### JWT Auth Middleware

```go
// middleware/auth.go
package middleware

import (
    "net/http"
    "strings"
    "github.com/labstack/echo/v4"
    "myapp/auth"
)

// JWTMiddleware validates the token and sets user info in context
func JWTMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        // ── Step 1: Get Authorization header ─────────────────
        authHeader := c.Request().Header.Get("Authorization")
        if authHeader == "" {
            return c.JSON(http.StatusUnauthorized, map[string]string{
                "error": "authorization header is required",
            })
        }

        // ── Step 2: Extract token (strip "Bearer ") ───────────
        parts := strings.SplitN(authHeader, " ", 2)
        if len(parts) != 2 || parts[0] != "Bearer" {
            return c.JSON(http.StatusUnauthorized, map[string]string{
                "error": "authorization header format: Bearer <token>",
            })
        }
        tokenStr := parts[1]

        // ── Step 3: Parse and validate token ──────────────────
        claims, err := auth.ParseToken(tokenStr)
        if err != nil {
            return c.JSON(http.StatusUnauthorized, map[string]string{
                "error": "invalid or expired token",
            })
        }

        // ── Step 4: Set claims in context for handlers ────────
        c.Set("user_id", claims.UserID)
        c.Set("email",   claims.Email)
        c.Set("role",    claims.Role)

        // ── Step 5: Call next handler ─────────────────────────
        return next(c)
    }
}
```

### Registering Protected Routes

```go
func main() {
    e := echo.New()
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())

    // ── Public routes — no auth needed ────────────────────────
    e.POST("/api/v1/auth/register", authHandler.Register)
    e.POST("/api/v1/auth/login",    authHandler.Login)
    e.POST("/api/v1/auth/refresh",  authHandler.RefreshToken)

    // ── Protected routes — JWT required ───────────────────────
    protected := e.Group("/api/v1")
    protected.Use(JWTMiddleware)

    protected.GET("/profile",          userHandler.GetProfile)
    protected.PUT("/profile",          userHandler.UpdateProfile)
    protected.GET("/users",            userHandler.GetUsers)
    protected.DELETE("/users/:id",     userHandler.DeleteUser)

    // ── Admin only routes ─────────────────────────────────────
    admin := e.Group("/api/v1/admin")
    admin.Use(JWTMiddleware)
    admin.Use(RoleMiddleware("admin"))

    admin.GET("/stats",       adminHandler.GetStats)
    admin.GET("/all-users",   adminHandler.GetAllUsers)
}
```

### Reading User from Context in Handler

```go
func (h *UserHandler) GetProfile(c echo.Context) error {
    // Get values set by JWTMiddleware
    userID := c.Get("user_id").(uint)
    email  := c.Get("email").(string)
    role   := c.Get("role").(string)

    var user models.User
    if err := h.db.First(&user, userID).Error; err != nil {
        return c.JSON(http.StatusNotFound, map[string]string{
            "error": "user not found",
        })
    }

    return c.JSON(http.StatusOK, user)
}
```

---

## Topic 4: User Registration & Login

### User Model

```go
// models/user.go
type User struct {
    gorm.Model
    Name      string `gorm:"size:100;not null"     json:"name"`
    Email     string `gorm:"uniqueIndex;not null"  json:"email"`
    Password  string `gorm:"not null"              json:"-"`    // never expose!
    Role      string `gorm:"size:20;default:'user'" json:"role"`
    IsActive  bool   `gorm:"default:true"          json:"is_active"`
}
```

### Registration Request & Response

```go
// Request DTO — what client sends
type RegisterRequest struct {
    Name     string `json:"name"     validate:"required,min=2,max=100"`
    Email    string `json:"email"    validate:"required,email"`
    Password string `json:"password" validate:"required,min=8"`
}

// Response DTO — what server returns (no password!)
type UserResponse struct {
    ID        uint      `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    Role      string    `json:"role"`
    CreatedAt time.Time `json:"created_at"`
}

// AuthResponse — returned after login/register
type AuthResponse struct {
    User         UserResponse `json:"user"`
    AccessToken  string       `json:"access_token"`
    RefreshToken string       `json:"refresh_token"`
    ExpiresIn    int64        `json:"expires_in"`
}
```

### Register Handler

```go
func (h *AuthHandler) Register(c echo.Context) error {
    // ── 1. Bind request ──────────────────────────────────────
    var req RegisterRequest
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid request body",
        })
    }

    // ── 2. Validate input ────────────────────────────────────
    if err := c.Validate(&req); err != nil {
        return c.JSON(http.StatusUnprocessableEntity, map[string]string{
            "error": err.Error(),
        })
    }

    // ── 3. Check email not already taken ─────────────────────
    var existing models.User
    if err := h.db.Where("email = ?", req.Email).First(&existing).Error; err == nil {
        return c.JSON(http.StatusConflict, map[string]string{
            "error": "email already registered",
        })
    }

    // ── 4. Hash password ─────────────────────────────────────
    hashedPassword, err := auth.HashPassword(req.Password)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not process password",
        })
    }

    // ── 5. Create user ───────────────────────────────────────
    user := models.User{
        Name:     req.Name,
        Email:    req.Email,
        Password: hashedPassword,
        Role:     "user",
    }
    if err := h.db.Create(&user).Error; err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not create user",
        })
    }

    // ── 6. Generate tokens ───────────────────────────────────
    tokens, err := auth.GenerateTokenPair(user.ID, user.Email, user.Role)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not generate token",
        })
    }

    // ── 7. Return response ───────────────────────────────────
    return c.JSON(http.StatusCreated, AuthResponse{
        User: UserResponse{
            ID: user.ID, Name: user.Name,
            Email: user.Email, Role: user.Role,
            CreatedAt: user.CreatedAt,
        },
        AccessToken:  tokens.AccessToken,
        RefreshToken: tokens.RefreshToken,
        ExpiresIn:    tokens.ExpiresIn,
    })
}
```

---

## Topic 5: Password Hashing (bcrypt)

### Why Hash Passwords?

Never store plain text passwords. If your database is breached, hashed passwords cannot be reversed. bcrypt adds a **salt** automatically (prevents rainbow table attacks) and is **slow by design** (prevents brute force).

### Install

```bash
go get golang.org/x/crypto/bcrypt
```

### Hash and Verify Password

```go
// auth/password.go
package auth

import "golang.org/x/crypto/bcrypt"

// HashPassword hashes a plain text password
// Cost 12 is recommended for production (higher = slower = more secure)
func HashPassword(password string) (string, error) {
    bytes, err := bcrypt.GenerateFromPassword([]byte(password), 12)
    if err != nil {
        return "", fmt.Errorf("HashPassword: %w", err)
    }
    return string(bytes), nil
}

// CheckPassword compares plain text with hashed password
// Returns nil if match, error if not
func CheckPassword(plainPassword, hashedPassword string) error {
    return bcrypt.CompareHashAndPassword(
        []byte(hashedPassword),
        []byte(plainPassword),
    )
}

// IsCorrectPassword returns bool for convenience
func IsCorrectPassword(plainPassword, hashedPassword string) bool {
    return bcrypt.CompareHashAndPassword(
        []byte(hashedPassword),
        []byte(plainPassword),
    ) == nil
}
```

### bcrypt Cost Factor

```go
// Cost factor controls how slow the hashing is
// Higher cost = slower = harder to brute force

bcrypt.MinCost     // 4  — testing only, very fast
bcrypt.DefaultCost // 10 — fine for most apps
                   // 12 — recommended for production
bcrypt.MaxCost     // 31 — extremely slow

// Each cost increase doubles the time
// Cost 10: ~100ms per hash
// Cost 12: ~400ms per hash
// Cost 14: ~1600ms per hash

// Usage
hash, _ := bcrypt.GenerateFromPassword([]byte(password), 12)

// bcrypt automatically embeds the salt in the hash
// Every call produces a DIFFERENT hash for the same password
// That's why you use CompareHashAndPassword, never compare strings directly

hash1, _ := bcrypt.GenerateFromPassword([]byte("secret"), 12)
hash2, _ := bcrypt.GenerateFromPassword([]byte("secret"), 12)
// hash1 != hash2  — different salts!
// But CompareHashAndPassword("secret", hash1) == nil  ✅
// And CompareHashAndPassword("secret", hash2) == nil  ✅
```

---

## Topic 6: Login with JWT

### Login Handler

```go
type LoginRequest struct {
    Email    string `json:"email"    validate:"required,email"`
    Password string `json:"password" validate:"required"`
}

func (h *AuthHandler) Login(c echo.Context) error {
    // ── 1. Bind request ──────────────────────────────────────
    var req LoginRequest
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid request body",
        })
    }

    // ── 2. Validate ──────────────────────────────────────────
    if err := c.Validate(&req); err != nil {
        return c.JSON(http.StatusUnprocessableEntity, map[string]string{
            "error": err.Error(),
        })
    }

    // ── 3. Find user by email ─────────────────────────────────
    var user models.User
    if err := h.db.Where("email = ?", req.Email).First(&user).Error; err != nil {
        // Use same error message for both "not found" and "wrong password"
        // This prevents user enumeration attacks
        return c.JSON(http.StatusUnauthorized, map[string]string{
            "error": "invalid email or password",
        })
    }

    // ── 4. Verify password ───────────────────────────────────
    if err := auth.CheckPassword(req.Password, user.Password); err != nil {
        return c.JSON(http.StatusUnauthorized, map[string]string{
            "error": "invalid email or password",
        })
    }

    // ── 5. Check if user is active ───────────────────────────
    if !user.IsActive {
        return c.JSON(http.StatusForbidden, map[string]string{
            "error": "account is deactivated",
        })
    }

    // ── 6. Generate tokens ───────────────────────────────────
    tokens, err := auth.GenerateTokenPair(user.ID, user.Email, user.Role)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not generate token",
        })
    }

    // ── 7. Return response ───────────────────────────────────
    return c.JSON(http.StatusOK, AuthResponse{
        User: UserResponse{
            ID: user.ID, Name: user.Name,
            Email: user.Email, Role: user.Role,
        },
        AccessToken:  tokens.AccessToken,
        RefreshToken: tokens.RefreshToken,
        ExpiresIn:    tokens.ExpiresIn,
    })
}
```

### Change Password Handler

```go
type ChangePasswordRequest struct {
    OldPassword string `json:"old_password" validate:"required"`
    NewPassword string `json:"new_password" validate:"required,min=8"`
}

func (h *AuthHandler) ChangePassword(c echo.Context) error {
    userID := c.Get("user_id").(uint)

    var req ChangePasswordRequest
    c.Bind(&req)
    c.Validate(&req)

    var user models.User
    h.db.First(&user, userID)

    // Verify current password
    if err := auth.CheckPassword(req.OldPassword, user.Password); err != nil {
        return c.JSON(http.StatusUnauthorized, map[string]string{
            "error": "current password is incorrect",
        })
    }

    // Hash new password
    newHash, err := auth.HashPassword(req.NewPassword)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not process password",
        })
    }

    // Update
    h.db.Model(&user).Update("password", newHash)

    return c.JSON(http.StatusOK, map[string]string{
        "message": "password changed successfully",
    })
}
```

---

## Topic 7: Role-Based Access Control

### What is RBAC?

**RBAC** (Role-Based Access Control) restricts access to resources based on the user's role. Instead of checking individual permissions per user, you assign roles and define what each role can do.

```
Roles:    admin  →  all permissions
          user   →  own resources only
          moderator → read all + edit content

Resources: GET /users      → admin, moderator
           POST /users     → admin only
           DELETE /users   → admin only
           GET /profile    → any authenticated user
           PUT /profile    → user (own profile)
```

### Role Middleware

```go
// middleware/role.go

// RoleMiddleware creates middleware that checks if user has one of the allowed roles
func RoleMiddleware(allowedRoles ...string) echo.MiddlewareFunc {
    return func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            // Get role set by JWTMiddleware
            role, ok := c.Get("role").(string)
            if !ok || role == "" {
                return c.JSON(http.StatusUnauthorized, map[string]string{
                    "error": "unauthorized",
                })
            }

            // Check if user's role is in allowed roles
            for _, allowed := range allowedRoles {
                if role == allowed {
                    return next(c)   // role matches — proceed
                }
            }

            // Role not allowed
            return c.JSON(http.StatusForbidden, map[string]string{
                "error": "you do not have permission to perform this action",
            })
        }
    }
}
```

### Using Role Middleware

```go
func setupRoutes(e *echo.Echo) {
    // Public
    e.POST("/api/auth/register", authHandler.Register)
    e.POST("/api/auth/login",    authHandler.Login)

    // Any authenticated user
    auth := e.Group("/api")
    auth.Use(JWTMiddleware)
    auth.GET("/profile",     userHandler.GetProfile)
    auth.PUT("/profile",     userHandler.UpdateProfile)

    // Admin only
    admin := e.Group("/api/admin")
    admin.Use(JWTMiddleware)
    admin.Use(RoleMiddleware("admin"))
    admin.GET("/users",          adminHandler.GetAllUsers)
    admin.DELETE("/users/:id",   adminHandler.DeleteUser)
    admin.GET("/stats",          adminHandler.GetStats)

    // Admin or Moderator
    moderated := e.Group("/api/content")
    moderated.Use(JWTMiddleware)
    moderated.Use(RoleMiddleware("admin", "moderator"))
    moderated.PUT("/posts/:id",  contentHandler.EditPost)
    moderated.DELETE("/posts/:id", contentHandler.DeletePost)
}
```

---

## Topic 8: Admin/User Roles

### Role Constants

```go
// Define roles as constants to avoid typos
const (
    RoleAdmin     = "admin"
    RoleUser      = "user"
    RoleModerator = "moderator"
)

// Validate role value
func IsValidRole(role string) bool {
    switch role {
    case RoleAdmin, RoleUser, RoleModerator:
        return true
    }
    return false
}
```

### Owner Check — User Can Only Edit Own Resources

```go
// Users can only update their OWN profile
func (h *UserHandler) UpdateProfile(c echo.Context) error {
    // ID from JWT (who is logged in)
    loggedInUserID := c.Get("user_id").(uint)

    // ID from URL param (who they want to edit)
    targetID, _ := strconv.Atoi(c.Param("id"))

    // Allow if: same user OR admin
    role := c.Get("role").(string)
    if uint(targetID) != loggedInUserID && role != RoleAdmin {
        return c.JSON(http.StatusForbidden, map[string]string{
            "error": "you can only update your own profile",
        })
    }

    // Proceed with update...
}
```

### Admin Assign Role Endpoint

```go
type AssignRoleRequest struct {
    Role string `json:"role" validate:"required,oneof=admin user moderator"`
}

// Only admin can change user roles
func (h *AdminHandler) AssignRole(c echo.Context) error {
    userID, _ := strconv.Atoi(c.Param("id"))

    var req AssignRoleRequest
    c.Bind(&req)
    c.Validate(&req)

    result := h.db.Model(&models.User{}).
        Where("id = ?", userID).
        Update("role", req.Role)

    if result.RowsAffected == 0 {
        return c.JSON(http.StatusNotFound, map[string]string{
            "error": "user not found",
        })
    }

    return c.JSON(http.StatusOK, map[string]string{
        "message": fmt.Sprintf("role updated to %s", req.Role),
    })
}
```

### Complete Auth Flow Summary

```
POST /auth/register  →  Register{name, email, password}
                     ←  {user, access_token, refresh_token}

POST /auth/login     →  Login{email, password}
                     ←  {user, access_token, refresh_token}

GET  /profile        →  Authorization: Bearer <access_token>
                     ←  {user profile data}

POST /auth/refresh   →  {refresh_token}
                     ←  {new access_token, new refresh_token}

PUT  /auth/password  →  Authorization: Bearer <token>
                        {old_password, new_password}
                     ←  {message: "password changed"}
```

---

## Topic 9: Email Sending

### Why Send Emails from API?

Common use cases:
- **Welcome email** after registration
- **Email verification** — confirm email ownership
- **Password reset** — send reset link
- **Order confirmation** — transactional emails
- **Notifications** — alerts and updates

### SMTP Configuration

```go
// config/config.go
type EmailConfig struct {
    SMTPHost     string
    SMTPPort     int
    SMTPUser     string   // your email address
    SMTPPassword string   // app password (not your login password!)
    FromName     string   // display name
    FromEmail    string   // from address
}

func LoadEmailConfig() EmailConfig {
    port, _ := strconv.Atoi(os.Getenv("SMTP_PORT"))
    return EmailConfig{
        SMTPHost:     os.Getenv("SMTP_HOST"),
        SMTPPort:     port,
        SMTPUser:     os.Getenv("SMTP_USER"),
        SMTPPassword: os.Getenv("SMTP_PASSWORD"),
        FromName:     os.Getenv("FROM_NAME"),
        FromEmail:    os.Getenv("FROM_EMAIL"),
    }
}
```

### Gmail SMTP Settings

```bash
# .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=yourapp@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password (not your login password)
FROM_NAME=MyApp
FROM_EMAIL=yourapp@gmail.com

# To get Gmail App Password:
# Google Account → Security → 2-Step Verification → App Passwords
# Generate a new app password for "Mail"
```

### Email Service Interface

```go
// email/service.go
package email

// EmailService defines what our email service can do
type EmailService interface {
    SendWelcome(to, name string) error
    SendPasswordReset(to, resetLink string) error
    SendVerification(to, verifyLink string) error
    SendRaw(to, subject, body string) error
}
```

---

## Topic 10: Using gomail for Sending Emails

### Install

```bash
go get gopkg.in/gomail.v2
```

### Basic Email with gomail

```go
package email

import (
    "fmt"
    "gopkg.in/gomail.v2"
)

type GomailService struct {
    host     string
    port     int
    username string
    password string
    from     string
    fromName string
}

func NewGomailService(cfg EmailConfig) *GomailService {
    return &GomailService{
        host:     cfg.SMTPHost,
        port:     cfg.SMTPPort,
        username: cfg.SMTPUser,
        password: cfg.SMTPPassword,
        from:     cfg.FromEmail,
        fromName: cfg.FromName,
    }
}

// send is the core send function used by all others
func (s *GomailService) send(to, subject, htmlBody string) error {
    m := gomail.NewMessage()

    // Set headers
    m.SetAddressHeader("From", s.from, s.fromName)
    m.SetHeader("To", to)
    m.SetHeader("Subject", subject)

    // Set HTML body
    m.SetBody("text/html", htmlBody)

    // Dial and send
    d := gomail.NewDialer(s.host, s.port, s.username, s.password)

    if err := d.DialAndSend(m); err != nil {
        return fmt.Errorf("email send failed: %w", err)
    }
    return nil
}
```

### Email Templates

```go
// Welcome Email
func (s *GomailService) SendWelcome(to, name string) error {
    subject := "Welcome to MyApp! 🎉"
    body := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h1 style="color: #333;">Welcome, %s! 👋</h1>
    <p>Thank you for registering with <strong>MyApp</strong>.</p>
    <p>Your account has been created successfully.</p>
    <a href="https://myapp.com/login"
       style="background:#4CAF50;color:white;padding:12px 24px;
              text-decoration:none;border-radius:4px;display:inline-block;">
        Get Started
    </a>
    <p style="color:#888;font-size:12px;margin-top:30px;">
        If you didn't register, please ignore this email.
    </p>
</body>
</html>`, name)

    return s.send(to, subject, body)
}

// Password Reset Email
func (s *GomailService) SendPasswordReset(to, resetLink string) error {
    subject := "Reset your MyApp password"
    body := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2>Password Reset Request</h2>
    <p>We received a request to reset your password.</p>
    <p>Click the button below to reset it. This link expires in <strong>1 hour</strong>.</p>
    <a href="%s"
       style="background:#e74c3c;color:white;padding:12px 24px;
              text-decoration:none;border-radius:4px;display:inline-block;">
        Reset Password
    </a>
    <p>Or copy this link:<br><small>%s</small></p>
    <p style="color:#888;font-size:12px;margin-top:30px;">
        If you didn't request this, ignore this email. Your password won't change.
    </p>
</body>
</html>`, resetLink, resetLink)

    return s.send(to, subject, body)
}

// Email Verification
func (s *GomailService) SendVerification(to, name, verifyLink string) error {
    subject := "Please verify your email address"
    body := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2>Hi %s, please verify your email</h2>
    <p>Click the button below to verify your email address.</p>
    <a href="%s"
       style="background:#3498db;color:white;padding:12px 24px;
              text-decoration:none;border-radius:4px;display:inline-block;">
        Verify Email
    </a>
    <p style="color:#888;font-size:12px;">This link expires in 24 hours.</p>
</body>
</html>`, name, verifyLink)

    return s.send(to, subject, body)
}
```

### Send Email with Attachment

```go
func (s *GomailService) SendWithAttachment(to, subject, body, filePath string) error {
    m := gomail.NewMessage()
    m.SetAddressHeader("From", s.from, s.fromName)
    m.SetHeader("To", to)
    m.SetHeader("Subject", subject)
    m.SetBody("text/html", body)

    // Attach a file
    m.Attach(filePath)

    // Attach with custom filename
    m.Attach("/path/to/file.pdf",
        gomail.Rename("invoice.pdf"),
        gomail.SetHeader(map[string][]string{
            "Content-Disposition": {"attachment; filename=\"invoice.pdf\""},
        }),
    )

    d := gomail.NewDialer(s.host, s.port, s.username, s.password)
    return d.DialAndSend(m)
}
```

### Send to Multiple Recipients

```go
func (s *GomailService) SendToMultiple(recipients []string, subject, body string) error {
    m := gomail.NewMessage()
    m.SetAddressHeader("From", s.from, s.fromName)

    // Multiple To addresses
    m.SetHeader("To", recipients...)

    // Or use BCC to hide recipient list from each other
    m.SetHeader("To", s.from)         // send to yourself
    m.SetHeader("Bcc", recipients...) // BCC everyone else

    m.SetHeader("Subject", subject)
    m.SetBody("text/html", body)

    d := gomail.NewDialer(s.host, s.port, s.username, s.password)
    return d.DialAndSend(m)
}
```

### Async Email Sending with Goroutine

```go
// Never block the HTTP handler waiting for email to send
// Send in background goroutine

func (h *AuthHandler) Register(c echo.Context) error {
    // ... create user ...

    // ✅ Send email in background — don't block response
    go func() {
        if err := h.emailService.SendWelcome(user.Email, user.Name); err != nil {
            log.Printf("ERROR: failed to send welcome email to %s: %v", user.Email, err)
            // Don't return error — email failure shouldn't fail registration
        }
    }()

    // Return response immediately — don't wait for email
    return c.JSON(http.StatusCreated, AuthResponse{...})
}
```

### Using Email Service in Handlers

```go
// Inject email service via constructor
type AuthHandler struct {
    db           *gorm.DB
    emailService email.EmailService
    cfg          *config.Config
}

func NewAuthHandler(db *gorm.DB, emailSvc email.EmailService, cfg *config.Config) *AuthHandler {
    return &AuthHandler{db: db, emailService: emailSvc, cfg: cfg}
}

// In main.go
func main() {
    // ...
    emailCfg := config.LoadEmailConfig()
    emailSvc := email.NewGomailService(emailCfg)
    authHandler := handlers.NewAuthHandler(db, emailSvc, cfg)
    // ...
}
```

---

## Interview Questions

### Topic 1–3: JWT & Middleware

**Q: What is JWT and how does it work?**
> JWT (JSON Web Token) is a signed token containing user claims (user_id, role, expiry). Server creates it at login, client sends it in every request header. Server verifies the signature on each request to authenticate without a DB lookup. Has 3 parts: Header.Payload.Signature, all base64-encoded.

**Q: What are the three parts of a JWT?**
> Header contains the algorithm (HS256) and token type. Payload contains claims — user data like user_id, email, role, and expiry. Signature is HMAC of encoded header+payload using the secret key. Tampering with the payload invalidates the signature.

**Q: What is the difference between Authentication and Authorization?**
> Authentication verifies WHO you are (login with JWT). Authorization verifies WHAT you can do (role check with RBAC). JWT handles authentication. Role middleware handles authorization. Both are needed for a secure API.

**Q: Where should you store a JWT on the client?**
> Options: httpOnly cookie (most secure — JS can't access, protects against XSS), localStorage (convenient but vulnerable to XSS attacks), sessionStorage (cleared on tab close). HttpOnly cookie + CSRF token is the most secure approach for web apps.

**Q: What happens when a JWT expires?**
> The server returns 401 Unauthorized. The client must use the refresh token to get a new access token via the refresh endpoint. If the refresh token is also expired, the user must log in again. This is why short-lived access tokens + long-lived refresh tokens are the standard pattern.

**Q: How does middleware work in Echo?**
> Middleware is a function that wraps a handler: `func(next HandlerFunc) HandlerFunc`. It runs before (and optionally after) the actual handler. Use `e.Use()` for global, or pass as 3rd arg to route for route-specific. Chain order matters — middleware runs in registration order.

### Topic 4–6: Registration, Login, bcrypt

**Q: Why use bcrypt for password hashing instead of SHA256 or MD5?**
> MD5/SHA256 are fast hash functions — an attacker can compute billions per second. bcrypt is intentionally slow (hundreds of milliseconds) making brute force attacks impractical. bcrypt also automatically adds a random salt — preventing rainbow table attacks. SHA256 without salt is dangerously fast.

**Q: What is a salt in bcrypt?**
> A random value added to the password before hashing. bcrypt generates and embeds it automatically in the hash. Even if two users have the same password, their hashes are different because of different salts. This means attackers can't use precomputed hash tables (rainbow tables).

**Q: Why return the same error for "wrong email" and "wrong password"?**
> User enumeration prevention. If you say "email not found" for wrong email and "wrong password" for correct email, attackers can figure out which emails are registered. Same error message for both makes it impossible to distinguish — a security best practice.

**Q: What is the difference between access token and refresh token?**
> Access token is short-lived (15min–1hr) — sent with every API request. Refresh token is long-lived (7–30 days) — used only to get a new access token when the old one expires. Keeping access tokens short-lived limits damage if one is stolen.

### Topic 7–8: RBAC & Roles

**Q: What is RBAC and how do you implement it in Go?**
> Role-Based Access Control restricts endpoints based on the user's role stored in the JWT. Implement with middleware: check `c.Get("role")` (set by JWT middleware) against the allowed roles for that route. Use `e.Group()` to apply role middleware to groups of routes.

**Q: How do you prevent a user from editing another user's data?**
> Owner check — compare the JWT's user_id with the resource's owner ID. In the handler: `if loggedInUserID != resourceOwnerID && role != "admin" { return 403 }`. Always verify ownership server-side — never trust the client to send the correct user ID.

### Topic 9–10: Email

**Q: Why send emails asynchronously with goroutines?**
> Email sending involves a network call to the SMTP server (100ms–2 seconds). Blocking the HTTP handler during this time degrades API response time. Sending in a goroutine returns the response immediately and emails are sent in the background. Log failures — don't let email errors fail the main operation.

**Q: What is an SMTP App Password and why use it?**
> For Gmail, your account password can't be used programmatically. App Passwords are special passwords generated for specific apps — they work with 2-factor auth enabled and can be revoked independently without changing your main password. Required for Gmail SMTP access.

---

## Quick Reference Cheatsheet

```go
// ── JWT GENERATE ────────────────────────────────────────────────
claims := JWTClaims{
    UserID: user.ID, Email: user.Email, Role: user.Role,
    RegisteredClaims: jwt.RegisteredClaims{
        ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
        IssuedAt:  jwt.NewNumericDate(time.Now()),
    },
}
token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
tokenStr, _ := token.SignedString([]byte(os.Getenv("JWT_SECRET")))

// ── JWT PARSE ──────────────────────────────────────────────────
token, err := jwt.ParseWithClaims(tokenStr, &JWTClaims{}, func(t *jwt.Token) (interface{}, error) {
    return []byte(os.Getenv("JWT_SECRET")), nil
})
claims := token.Claims.(*JWTClaims)

// ── BCRYPT ─────────────────────────────────────────────────────
hash, _  := bcrypt.GenerateFromPassword([]byte(password), 12)
err      := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
// err == nil → password matches

// ── JWT MIDDLEWARE ─────────────────────────────────────────────
func JWTMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        token := strings.TrimPrefix(c.Request().Header.Get("Authorization"), "Bearer ")
        claims, err := auth.ParseToken(token)
        if err != nil { return c.JSON(401, map[string]string{"error": "unauthorized"}) }
        c.Set("user_id", claims.UserID)
        c.Set("role", claims.Role)
        return next(c)
    }
}

// ── ROLE MIDDLEWARE ────────────────────────────────────────────
func RoleMiddleware(roles ...string) echo.MiddlewareFunc {
    return func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            role := c.Get("role").(string)
            for _, r := range roles {
                if role == r { return next(c) }
            }
            return c.JSON(403, map[string]string{"error": "forbidden"})
        }
    }
}

// ── ROUTES SETUP ───────────────────────────────────────────────
e.POST("/auth/register", h.Register)      // public
e.POST("/auth/login",    h.Login)          // public

protected := e.Group("/api")
protected.Use(JWTMiddleware)               // all need auth

admin := e.Group("/admin")
admin.Use(JWTMiddleware, RoleMiddleware("admin"))  // admin only

// ── GOMAIL ─────────────────────────────────────────────────────
m := gomail.NewMessage()
m.SetAddressHeader("From", "from@example.com", "MyApp")
m.SetHeader("To", "to@example.com")
m.SetHeader("Subject", "Hello!")
m.SetBody("text/html", "<h1>Hello</h1>")
m.Attach("/path/to/file.pdf")             // optional attachment

d := gomail.NewDialer("smtp.gmail.com", 587, "user", "apppassword")
d.DialAndSend(m)

// ── ASYNC EMAIL ────────────────────────────────────────────────
go func() {
    if err := emailSvc.SendWelcome(user.Email, user.Name); err != nil {
        log.Printf("email failed: %v", err)
    }
}()
```

---

## Resources

- [golang-jwt/jwt GitHub](https://github.com/golang-jwt/jwt)
- [bcrypt GoDoc](https://pkg.go.dev/golang.org/x/crypto/bcrypt)
- [gomail GoDoc](https://pkg.go.dev/gopkg.in/gomail.v2)
- [Echo Middleware Docs](https://echo.labstack.com/docs/middleware)
- [OWASP Authentication Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

*Phase 2 — JWT Auth · bcrypt · RBAC · Email Sending — All 10 Topics Covered ✅*