# 🐹 Go Language — Phase 2 Study Notes

> Complete notes for:
> - **Topic 1: Rate Limiting & Caching**
> - **Topic 2: Redis Integration**
> - **Topic 3: API Rate Limiting**
> - **Topic 4: Background Jobs & Cron Jobs**
> - **Topic 5: robfig/cron for Scheduled Tasks**
> - **Topic 6: Testing in Go**
> - **Topic 7: Unit Tests**
> - **Topic 8: API Integration Tests**
> - **Topic 9: Dockerizing the Go App**

---

## 📚 Table of Contents

- [Topic 1: Rate Limiting & Caching](#topic-1-rate-limiting--caching)
- [Topic 2: Redis Integration](#topic-2-redis-integration)
- [Topic 3: API Rate Limiting](#topic-3-api-rate-limiting)
- [Topic 4: Background Jobs & Cron Jobs](#topic-4-background-jobs--cron-jobs)
- [Topic 5: robfig/cron for Scheduled Tasks](#topic-5-robfigcron-for-scheduled-tasks)
- [Topic 6: Testing in Go](#topic-6-testing-in-go)
- [Topic 7: Unit Tests](#topic-7-unit-tests)
- [Topic 8: API Integration Tests](#topic-8-api-integration-tests)
- [Topic 9: Dockerizing the Go App](#topic-9-dockerizing-the-go-app)
- [Interview Questions](#interview-questions)
- [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Topic 1: Rate Limiting & Caching

### What is Rate Limiting?

Rate limiting restricts how many requests a client can make in a given time window. It protects your API from:
- **DDoS attacks** — overwhelming the server
- **Brute force attacks** — trying many passwords
- **API abuse** — scraping or over-usage
- **Resource exhaustion** — preventing fair use for others

### Rate Limiting Algorithms

| Algorithm | How it works | Best for |
|---|---|---|
| **Fixed Window** | Count requests per time window (1min, 1hr) | Simple use cases |
| **Sliding Window** | Rolling time window, more accurate | General APIs |
| **Token Bucket** | Tokens refill at fixed rate, consume 1 per request | Bursty traffic allowed |
| **Leaky Bucket** | Queue requests, process at fixed rate | Smoothing traffic spikes |

### What is Caching?

Caching stores frequently accessed data in fast memory (Redis) so repeated requests don't hit the database:

```
Without cache:  Request → API → Database → Response  (~50-200ms)
With cache:     Request → API → Redis    → Response  (~1-5ms)
```

**Cache use cases:**
- User profile data (read often, changes rarely)
- Product listings and categories
- Computed statistics and dashboards
- JWT token blacklists
- Session data
- API responses for public endpoints

---

## Topic 2: Redis Integration

### What is Redis?

Redis (Remote Dictionary Server) is an in-memory key-value store. It's extremely fast (~microseconds) because all data lives in RAM.

```
Redis data structures:
  String   → "user:1" = "{"name":"Rahul"}"
  Hash     → "user:1" = {name:"Rahul", email:"..."} 
  List     → "queue:emails" = ["job1", "job2"]
  Set      → "online_users" = {1, 5, 23}
  ZSet     → "leaderboard" = {player1:100, player2:95}
  Expire   → any key can have a TTL (time to live)
```

### Install go-redis

```bash
go get github.com/redis/go-redis/v9
```

### Connect to Redis

```go
// config/redis.go
package config

import (
    "context"
    "fmt"
    "os"

    "github.com/redis/go-redis/v9"
)

var RedisClient *redis.Client

func ConnectRedis() {
    RedisClient = redis.NewClient(&redis.Options{
        Addr:     fmt.Sprintf("%s:%s", os.Getenv("REDIS_HOST"), os.Getenv("REDIS_PORT")),
        Password: os.Getenv("REDIS_PASSWORD"), // "" if no password
        DB:       0,                            // default DB
        PoolSize: 10,                           // connection pool size
    })

    // Test connection
    ctx := context.Background()
    if err := RedisClient.Ping(ctx).Err(); err != nil {
        log.Fatal("Redis connection failed:", err)
    }
    log.Println("Redis connected!")
}
```

### Basic Redis Operations

```go
import (
    "context"
    "time"
    "github.com/redis/go-redis/v9"
)

var ctx = context.Background()

// ── SET — store a value with optional TTL ─────────────────────
rdb.Set(ctx, "key", "value", 0)                    // no expiry
rdb.Set(ctx, "session:abc", userID, 24*time.Hour)  // expires in 24h
rdb.Set(ctx, "otp:user:1", "123456", 5*time.Minute) // 5 min TTL

// ── GET — retrieve a value ────────────────────────────────────
val, err := rdb.Get(ctx, "key").Result()
if err == redis.Nil {
    fmt.Println("key does not exist")
} else if err != nil {
    log.Printf("Redis GET error: %v", err)
} else {
    fmt.Println("Value:", val)
}

// ── DEL — delete a key ────────────────────────────────────────
rdb.Del(ctx, "key")
rdb.Del(ctx, "key1", "key2", "key3")  // delete multiple

// ── EXISTS — check if key exists ──────────────────────────────
n, _ := rdb.Exists(ctx, "key").Result()
if n > 0 {
    fmt.Println("key exists")
}

// ── EXPIRE — set/update TTL on existing key ───────────────────
rdb.Expire(ctx, "key", 10*time.Minute)

// ── TTL — get remaining time ──────────────────────────────────
ttl, _ := rdb.TTL(ctx, "key").Result()
fmt.Println("Expires in:", ttl)

// ── INCR / DECR — atomic counter ─────────────────────────────
rdb.Incr(ctx, "page_views")           // +1
rdb.IncrBy(ctx, "page_views", 5)      // +5
rdb.Decr(ctx, "stock:product:1")      // -1
```

### Caching Pattern — Cache-Aside (Lazy Loading)

```go
// services/user_service.go
package services

import (
    "context"
    "encoding/json"
    "fmt"
    "time"
    "github.com/redis/go-redis/v9"
    "gorm.io/gorm"
)

type UserService struct {
    db  *gorm.DB
    rdb *redis.Client
}

func (s *UserService) GetUserByID(id uint) (*models.User, error) {
    ctx := context.Background()
    cacheKey := fmt.Sprintf("user:%d", id)

    // ── Step 1: Try cache first ───────────────────────────────
    cached, err := s.rdb.Get(ctx, cacheKey).Result()
    if err == nil {
        // Cache HIT — unmarshal and return
        var user models.User
        if err := json.Unmarshal([]byte(cached), &user); err == nil {
            return &user, nil
        }
    }

    // ── Step 2: Cache MISS — query database ───────────────────
    var user models.User
    if err := s.db.First(&user, id).Error; err != nil {
        return nil, err
    }

    // ── Step 3: Store in cache for next time ──────────────────
    userJSON, _ := json.Marshal(user)
    s.rdb.Set(ctx, cacheKey, userJSON, 15*time.Minute) // cache 15 min

    return &user, nil
}

// Invalidate cache when user is updated
func (s *UserService) UpdateUser(id uint, updates map[string]interface{}) error {
    if err := s.db.Model(&models.User{}).Where("id = ?", id).Updates(updates).Error; err != nil {
        return err
    }

    // Delete cache so next read gets fresh data
    cacheKey := fmt.Sprintf("user:%d", id)
    s.rdb.Del(context.Background(), cacheKey)
    return nil
}
```

### Cache List Response

```go
func (s *UserService) GetAllUsers(page, limit int) ([]models.User, int64, error) {
    ctx := context.Background()
    cacheKey := fmt.Sprintf("users:page:%d:limit:%d", page, limit)

    // Try cache
    cached, err := s.rdb.Get(ctx, cacheKey).Result()
    if err == nil {
        var result struct {
            Users []models.User `json:"users"`
            Total int64         `json:"total"`
        }
        json.Unmarshal([]byte(cached), &result)
        return result.Users, result.Total, nil
    }

    // DB query
    var users []models.User
    var total int64
    s.db.Model(&models.User{}).Count(&total)
    s.db.Offset((page-1)*limit).Limit(limit).Find(&users)

    // Cache for 5 minutes
    data, _ := json.Marshal(map[string]interface{}{
        "users": users, "total": total,
    })
    s.rdb.Set(ctx, cacheKey, data, 5*time.Minute)

    return users, total, nil
}
```

---

## Topic 3: API Rate Limiting

### Rate Limiting with Echo Built-in Middleware

```go
import "github.com/labstack/echo/v4/middleware"

// Simple in-memory rate limiter
// 20 requests per second per IP
e.Use(middleware.RateLimiter(
    middleware.NewRateLimiterMemoryStore(20),
))
```

### Custom Rate Limiter with Redis

```go
// middleware/rate_limiter.go
package middleware

import (
    "context"
    "fmt"
    "net/http"
    "time"

    "github.com/labstack/echo/v4"
    "github.com/redis/go-redis/v9"
)

type RateLimitConfig struct {
    Limit  int           // max requests
    Window time.Duration // time window
}

// RateLimitMiddleware limits requests per IP using Redis
func RateLimitMiddleware(rdb *redis.Client, cfg RateLimitConfig) echo.MiddlewareFunc {
    return func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            ctx := context.Background()

            // Use client IP as key
            ip  := c.RealIP()
            key := fmt.Sprintf("rate_limit:%s", ip)

            // Increment counter
            count, err := rdb.Incr(ctx, key).Result()
            if err != nil {
                // Redis error — allow request (fail open)
                return next(c)
            }

            // Set expiry only on first request in window
            if count == 1 {
                rdb.Expire(ctx, key, cfg.Window)
            }

            // Add rate limit headers
            remaining := cfg.Limit - int(count)
            if remaining < 0 { remaining = 0 }
            c.Response().Header().Set("X-RateLimit-Limit",     fmt.Sprintf("%d", cfg.Limit))
            c.Response().Header().Set("X-RateLimit-Remaining", fmt.Sprintf("%d", remaining))

            // Check if limit exceeded
            if count > int64(cfg.Limit) {
                ttl, _ := rdb.TTL(ctx, key).Result()
                c.Response().Header().Set("Retry-After", fmt.Sprintf("%.0f", ttl.Seconds()))
                return c.JSON(http.StatusTooManyRequests, map[string]string{
                    "error":   "rate limit exceeded",
                    "message": fmt.Sprintf("try again in %.0f seconds", ttl.Seconds()),
                })
            }

            return next(c)
        }
    }
}
```

### Different Limits for Different Routes

```go
func main() {
    e := echo.New()

    strictCfg := RateLimitConfig{Limit: 5,   Window: time.Minute} // 5/min
    normalCfg := RateLimitConfig{Limit: 100, Window: time.Minute} // 100/min
    looseCfg  := RateLimitConfig{Limit: 500, Window: time.Minute} // 500/min

    // Auth routes — very strict (prevent brute force)
    auth := e.Group("/api/auth")
    auth.Use(RateLimitMiddleware(rdb, strictCfg))
    auth.POST("/login",    h.Login)
    auth.POST("/register", h.Register)

    // API routes — normal limit
    api := e.Group("/api")
    api.Use(JWTMiddleware, RateLimitMiddleware(rdb, normalCfg))
    api.GET("/users",    h.GetUsers)
    api.POST("/users",   h.CreateUser)

    // Public read-only — loose limit
    public := e.Group("/public")
    public.Use(RateLimitMiddleware(rdb, looseCfg))
    public.GET("/products", h.GetProducts)
}
```

---

## Topic 4: Background Jobs & Cron Jobs

### What are Background Jobs?

Background jobs are tasks that run **outside the HTTP request cycle** — the client doesn't wait for them.

```
Without background job:
  Client → POST /register → [create user] → [send email 2s] → Response  (slow!)

With background job:
  Client → POST /register → [create user] → Response  (fast!)
                                          ↓ goroutine
                                    [send email in background]
```

**Common background job use cases:**
- Sending welcome/notification emails
- Generating reports and PDFs
- Processing uploaded images (resize, compress)
- Syncing data with external services
- Sending push notifications
- Cleaning up old records
- Recalculating statistics

### Simple Background Job with Goroutine

```go
// Simplest form — fire and forget
func (h *AuthHandler) Register(c echo.Context) error {
    // ... create user ...

    // Non-blocking background task
    go func() {
        if err := h.emailSvc.SendWelcome(user.Email, user.Name); err != nil {
            log.Printf("ERROR sending welcome email to %s: %v", user.Email, err)
        }
    }()

    return c.JSON(http.StatusCreated, user)
}
```

### Job Queue Pattern with Channels

```go
// jobs/queue.go
package jobs

import (
    "fmt"
    "log"
)

// Job represents a unit of work
type Job struct {
    Type    string
    Payload map[string]interface{}
}

// JobQueue manages background workers
type JobQueue struct {
    queue   chan Job
    workers int
}

func NewJobQueue(workers, bufferSize int) *JobQueue {
    jq := &JobQueue{
        queue:   make(chan Job, bufferSize),
        workers: workers,
    }
    jq.start()
    return jq
}

// Start launches N worker goroutines
func (jq *JobQueue) start() {
    for i := 0; i < jq.workers; i++ {
        go func(workerID int) {
            for job := range jq.queue {
                log.Printf("Worker %d processing job: %s", workerID, job.Type)
                if err := processJob(job); err != nil {
                    log.Printf("Worker %d job %s failed: %v", workerID, job.Type, err)
                }
            }
        }(i)
    }
}

// Enqueue adds a job to the queue
func (jq *JobQueue) Enqueue(job Job) error {
    select {
    case jq.queue <- job:
        return nil
    default:
        return fmt.Errorf("job queue is full")
    }
}

// Process different job types
func processJob(job Job) error {
    switch job.Type {
    case "send_welcome_email":
        email := job.Payload["email"].(string)
        name  := job.Payload["name"].(string)
        return sendWelcomeEmail(email, name)

    case "resize_image":
        path := job.Payload["path"].(string)
        return resizeImage(path)

    case "generate_report":
        userID := job.Payload["user_id"].(float64)
        return generateReport(int(userID))

    default:
        return fmt.Errorf("unknown job type: %s", job.Type)
    }
}

// In main.go
var jobQueue = jobs.NewJobQueue(5, 100)  // 5 workers, buffer 100

// In handler
jobQueue.Enqueue(jobs.Job{
    Type: "send_welcome_email",
    Payload: map[string]interface{}{
        "email": user.Email,
        "name":  user.Name,
    },
})
```

---

## Topic 5: robfig/cron for Scheduled Tasks

### What are Cron Jobs?

Cron jobs are tasks scheduled to run **automatically at specific times** — like crontab in Linux but in Go code.

**Common cron job use cases:**
- Generate daily/weekly reports at midnight
- Send reminder emails every morning
- Clean up expired sessions/tokens every hour
- Sync data with external API every 15 minutes
- Backup database every night
- Send newsletters every Sunday

### Install

```bash
go get github.com/robfig/cron/v3
```

### Cron Expression Format

```
┌──────────── Second (0–59)       [optional]
│ ┌────────── Minute (0–59)
│ │ ┌──────── Hour (0–23)
│ │ │ ┌────── Day of month (1–31)
│ │ │ │ ┌──── Month (1–12 or Jan–Dec)
│ │ │ │ │ ┌── Day of week (0–6, Sun=0 or Sun–Sat)
│ │ │ │ │ │
* * * * * *

Examples:
"0 * * * *"       → every hour (at minute 0)
"0 0 * * *"       → every day at midnight
"0 9 * * 1"       → every Monday at 9:00 AM
"0 0 1 * *"       → first day of every month
"*/15 * * * *"    → every 15 minutes
"0 8,12,18 * * *" → at 8AM, 12PM, 6PM daily

Predefined (without second field):
@yearly   = "0 0 1 1 *"
@monthly  = "0 0 1 * *"
@weekly   = "0 0 * * 0"
@daily    = "0 0 * * *"
@hourly   = "0 * * * *"
@every 30s / @every 5m / @every 1h  (duration strings)
```

### Basic Cron Setup

```go
// cron/scheduler.go
package cron

import (
    "log"
    "github.com/robfig/cron/v3"
    "gorm.io/gorm"
)

type Scheduler struct {
    c  *cron.Cron
    db *gorm.DB
}

func NewScheduler(db *gorm.DB) *Scheduler {
    // WithSeconds() enables 6-field cron (with seconds)
    c := cron.New(cron.WithSeconds())
    return &Scheduler{c: c, db: db}
}

func (s *Scheduler) RegisterJobs() {
    // Every day at midnight — delete expired tokens
    s.c.AddFunc("0 0 0 * * *", func() {
        log.Println("CRON: Cleaning expired tokens...")
        s.db.Where("expires_at < NOW()").Delete(&models.Token{})
        log.Println("CRON: Expired tokens cleaned")
    })

    // Every Monday at 8:00 AM — send weekly report
    s.c.AddFunc("0 0 8 * * 1", func() {
        log.Println("CRON: Sending weekly report...")
        if err := s.sendWeeklyReport(); err != nil {
            log.Printf("CRON ERROR: weekly report failed: %v", err)
        }
    })

    // Every 15 minutes — sync product prices from external API
    s.c.AddFunc("0 */15 * * * *", func() {
        log.Println("CRON: Syncing product prices...")
        if err := s.syncProductPrices(); err != nil {
            log.Printf("CRON ERROR: price sync failed: %v", err)
        }
    })

    // Every hour — recalculate statistics
    s.c.AddFunc("@hourly", func() {
        log.Println("CRON: Recalculating stats...")
        s.recalculateStats()
    })

    // Every 30 seconds — health check
    s.c.AddFunc("@every 30s", func() {
        s.healthCheck()
    })
}

func (s *Scheduler) Start() {
    s.c.Start()
    log.Println("Cron scheduler started")
}

func (s *Scheduler) Stop() {
    s.c.Stop()
    log.Println("Cron scheduler stopped")
}
```

### Using Cron in main.go

```go
func main() {
    // ... setup db, echo ...

    // Start cron scheduler
    scheduler := cron.NewScheduler(db)
    scheduler.RegisterJobs()
    scheduler.Start()
    defer scheduler.Stop()  // graceful shutdown

    // Start HTTP server
    e.Logger.Fatal(e.Start(":8080"))
}
```

### Cron Job with Error Handling and Logging

```go
func (s *Scheduler) sendWeeklyReport() error {
    start := time.Now()
    log.Println("CRON[weekly_report]: started")

    // Get all active users
    var users []models.User
    if err := s.db.Where("is_active = ?", true).Find(&users).Error; err != nil {
        return fmt.Errorf("fetch users: %w", err)
    }

    successCount, failCount := 0, 0
    for _, user := range users {
        if err := s.emailSvc.SendWeeklyReport(user.Email, user.Name); err != nil {
            log.Printf("CRON[weekly_report]: failed for %s: %v", user.Email, err)
            failCount++
        } else {
            successCount++
        }
    }

    log.Printf("CRON[weekly_report]: done in %v — success:%d failed:%d",
        time.Since(start), successCount, failCount)
    return nil
}
```

---

## Topic 6: Testing in Go

### Go Testing Basics

Go has a built-in `testing` package — no external test runner needed.

```
File naming:   handlers/user.go      → handlers/user_test.go
Function name: Test + FunctionName   → TestGetUser, TestCreateUser
Run tests:     go test ./...          → run all tests
               go test -v ./...       → verbose output
               go test -run TestGetUser ./... → run specific test
               go test -cover ./...   → show coverage %
               go test -race ./...    → detect race conditions
```

### Test File Structure

```go
// handlers/user_test.go
package handlers_test   // use _test suffix for black-box testing

import (
    "testing"
)

// Test function must start with "Test" + capital letter
func TestFunctionName(t *testing.T) {
    // Arrange — set up test data
    // Act     — call the function
    // Assert  — check the result
}
```

### Testing Assertions

```go
func TestAdd(t *testing.T) {
    result := Add(2, 3)

    // t.Errorf — marks test as failed but continues
    if result != 5 {
        t.Errorf("expected 5, got %d", result)
    }

    // t.Fatalf — marks test as failed and STOPS the test
    if result != 5 {
        t.Fatalf("expected 5, got %d — cannot continue", result)
    }

    // t.Logf — logs info (shown with -v flag)
    t.Logf("Add(2,3) = %d", result)
}
```

### testify — Better Assertions

```bash
go get github.com/stretchr/testify
```

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestUser(t *testing.T) {
    user := User{ID: 1, Name: "Rahul", Email: "rahul@example.com"}

    // assert — continues test on failure
    assert.Equal(t, 1, user.ID)
    assert.Equal(t, "Rahul", user.Name)
    assert.NotEmpty(t, user.Email)
    assert.True(t, user.IsActive)
    assert.Nil(t, user.DeletedAt)
    assert.Contains(t, user.Email, "@")

    // require — STOPS test on failure (use for critical checks)
    require.NotNil(t, user)
    require.Equal(t, 1, user.ID)
}
```

### Table-Driven Tests

```go
// Best practice — test many cases cleanly
func TestDivide(t *testing.T) {
    tests := []struct {
        name     string
        a, b     float64
        expected float64
        wantErr  bool
    }{
        {name: "normal division",      a: 10, b: 2,  expected: 5,  wantErr: false},
        {name: "divide by zero",       a: 10, b: 0,  expected: 0,  wantErr: true},
        {name: "negative numbers",     a: -6, b: 2,  expected: -3, wantErr: false},
        {name: "decimal result",       a: 7,  b: 2,  expected: 3.5,wantErr: false},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Divide(tt.a, tt.b)

            if tt.wantErr {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
                assert.Equal(t, tt.expected, result)
            }
        })
    }
}
```

---

## Topic 7: Unit Tests

### Unit Testing Service Layer

```go
// services/user_service_test.go
package services_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
)

// ── Mock the repository (database) ───────────────────────────
type MockUserRepo struct {
    mock.Mock
}

func (m *MockUserRepo) FindByID(id uint) (*models.User, error) {
    args := m.Called(id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepo) Create(user *models.User) error {
    args := m.Called(user)
    return args.Error(0)
}

// ── Tests ─────────────────────────────────────────────────────

func TestUserService_GetUserByID_Found(t *testing.T) {
    // Arrange
    mockRepo := new(MockUserRepo)
    service  := services.NewUserService(mockRepo)

    expectedUser := &models.User{ID: 1, Name: "Rahul", Email: "rahul@example.com"}
    mockRepo.On("FindByID", uint(1)).Return(expectedUser, nil)

    // Act
    user, err := service.GetUserByID(1)

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, "Rahul", user.Name)
    assert.Equal(t, "rahul@example.com", user.Email)
    mockRepo.AssertExpectations(t) // verify mock was called as expected
}

func TestUserService_GetUserByID_NotFound(t *testing.T) {
    mockRepo := new(MockUserRepo)
    service  := services.NewUserService(mockRepo)

    mockRepo.On("FindByID", uint(99)).Return(nil, errors.New("not found"))

    user, err := service.GetUserByID(99)

    assert.Error(t, err)
    assert.Nil(t, user)
}

func TestUserService_CreateUser_Success(t *testing.T) {
    mockRepo := new(MockUserRepo)
    service  := services.NewUserService(mockRepo)

    mockRepo.On("Create", mock.AnythingOfType("*models.User")).Return(nil)

    err := service.CreateUser("Rahul", "rahul@example.com", "password123")

    assert.NoError(t, err)
    mockRepo.AssertExpectations(t)
}
```

### Testing Pure Functions (No Mocks Needed)

```go
// auth/password_test.go
package auth_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "myapp/auth"
)

func TestHashPassword(t *testing.T) {
    password := "mysecretpassword"

    hash, err := auth.HashPassword(password)

    assert.NoError(t, err)
    assert.NotEmpty(t, hash)
    assert.NotEqual(t, password, hash)      // hash != original
    assert.Greater(t, len(hash), 20)        // hash is long
}

func TestCheckPassword_Correct(t *testing.T) {
    password := "mysecretpassword"
    hash, _  := auth.HashPassword(password)

    err := auth.CheckPassword(password, hash)

    assert.NoError(t, err)
}

func TestCheckPassword_Wrong(t *testing.T) {
    hash, _ := auth.HashPassword("correctpassword")

    err := auth.CheckPassword("wrongpassword", hash)

    assert.Error(t, err)
}

func TestHashPassword_DifferentEachTime(t *testing.T) {
    password := "samepassword"
    hash1, _ := auth.HashPassword(password)
    hash2, _ := auth.HashPassword(password)

    // Same password → different hashes (because of salt)
    assert.NotEqual(t, hash1, hash2)
}
```

### Test Setup and Teardown

```go
func TestMain(m *testing.M) {
    // Setup — runs before all tests in this package
    fmt.Println("Setting up test environment...")
    setupTestDB()

    // Run tests
    code := m.Run()

    // Teardown — runs after all tests
    fmt.Println("Cleaning up...")
    cleanupTestDB()

    os.Exit(code)
}

// Per-test setup with t.Cleanup
func TestCreateUser(t *testing.T) {
    // Setup for this specific test
    user := createTestUser(t)

    // Cleanup runs when test finishes (even on failure)
    t.Cleanup(func() {
        deleteTestUser(user.ID)
    })

    // ... test code ...
}
```

---

## Topic 8: API Integration Tests

### Integration Test with httptest

```go
// handlers/user_handler_test.go
package handlers_test

import (
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "strings"
    "testing"

    "github.com/labstack/echo/v4"
    "github.com/stretchr/testify/assert"
)

// Setup Echo for testing
func setupTestEcho() *echo.Echo {
    e := echo.New()
    e.Use(middleware.Logger())
    return e
}

// Test GET /users
func TestGetUsers(t *testing.T) {
    // Arrange
    e   := setupTestEcho()
    rec := httptest.NewRecorder()
    req := httptest.NewRequest(http.MethodGet, "/users", nil)
    req.Header.Set("Content-Type", "application/json")

    handler := &UserHandler{db: testDB}
    c := e.NewContext(req, rec)

    // Act
    err := handler.GetUsers(c)

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, http.StatusOK, rec.Code)

    // Parse response body
    var response []models.User
    err = json.Unmarshal(rec.Body.Bytes(), &response)
    assert.NoError(t, err)
}

// Test POST /users
func TestCreateUser(t *testing.T) {
    e   := setupTestEcho()
    rec := httptest.NewRecorder()

    // Request body
    body := `{"name":"Rahul","email":"rahul@test.com","password":"secret123"}`
    req  := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")

    handler := &UserHandler{db: testDB}
    c := e.NewContext(req, rec)

    // Act
    err := handler.CreateUser(c)

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, http.StatusCreated, rec.Code)

    var created models.User
    json.Unmarshal(rec.Body.Bytes(), &created)
    assert.Equal(t, "Rahul", created.Name)
    assert.NotZero(t, created.ID)
}

// Test with JWT token in header
func TestGetProfile_Authenticated(t *testing.T) {
    e   := setupTestEcho()
    rec := httptest.NewRecorder()
    req := httptest.NewRequest(http.MethodGet, "/profile", nil)

    // Add JWT to request
    token, _ := auth.GenerateToken(1, "rahul@test.com", "user")
    req.Header.Set("Authorization", "Bearer "+token)

    handler := &UserHandler{db: testDB}
    c := e.NewContext(req, rec)

    // Simulate middleware setting user context
    c.Set("user_id", uint(1))
    c.Set("role", "user")

    err := handler.GetProfile(c)

    assert.NoError(t, err)
    assert.Equal(t, http.StatusOK, rec.Code)
}

// Test validation error
func TestCreateUser_ValidationFail(t *testing.T) {
    e   := setupTestEcho()
    rec := httptest.NewRecorder()

    // Missing required fields
    body := `{"name":""}`
    req  := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")

    handler := &UserHandler{db: testDB}
    c := e.NewContext(req, rec)

    err := handler.CreateUser(c)

    assert.NoError(t, err)
    assert.Equal(t, http.StatusBadRequest, rec.Code)
}
```

### Test Database Setup

```go
// testutils/db.go
package testutils

import (
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "os"
)

var TestDB *gorm.DB

func SetupTestDB() *gorm.DB {
    dsn := os.Getenv("TEST_DATABASE_URL")
    if dsn == "" {
        dsn = "postgresql://postgres:secret@localhost:5432/myapp_test?sslmode=disable"
    }

    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        panic("failed to connect to test database: " + err.Error())
    }

    // Run migrations
    db.AutoMigrate(&models.User{}, &models.Product{})
    return db
}

// CleanDB removes all test data between tests
func CleanDB(db *gorm.DB) {
    db.Exec("TRUNCATE TABLE users, products RESTART IDENTITY CASCADE")
}
```

---

## Topic 9: Dockerizing the Go App

### Why Docker?

Docker packages your app with all its dependencies into a container that runs identically on any machine — no "works on my machine" problems.

```
Without Docker:  Install Go, set GOPATH, install PostgreSQL, Redis...
With Docker:     docker-compose up   (everything starts!)
```

### Dockerfile for Go

```dockerfile
# Dockerfile

# ── Stage 1: Build ────────────────────────────────────────────
FROM golang:1.21-alpine AS builder

# Install dependencies
RUN apk add --no-cache git

# Set working directory
WORKDIR /app

# Copy go.mod and go.sum first (for Docker layer caching)
COPY go.mod go.sum ./

# Download dependencies (cached if go.mod unchanged)
RUN go mod download

# Copy source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd/main.go

# ── Stage 2: Run ──────────────────────────────────────────────
# Use minimal image — much smaller than golang image
FROM alpine:latest

# Install certificates (needed for HTTPS calls)
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy only the binary from builder stage
COPY --from=builder /app/main .

# Copy .env.example (not .env!)
COPY --from=builder /app/.env.example .

# Expose port
EXPOSE 8080

# Run the binary
CMD ["./main"]
```

### .dockerignore

```
# .dockerignore — files NOT copied into Docker image
.git
.gitignore
.env
.env.local
*.md
Dockerfile
docker-compose.yml
uploads/
*.test
```

### docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ── Go API ────────────────────────────────────────────────────
  api:
    build: .
    container_name: myapp-api
    ports:
      - "8080:8080"
    environment:
      - APP_ENV=production
      - SERVER_PORT=8080
      - DB_HOST=postgres        # container name, not localhost!
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=secret
      - DB_NAME=myapp
      - DB_SSLMODE=disable
      - REDIS_HOST=redis        # container name
      - REDIS_PORT=6379
      - JWT_SECRET=my-super-secret-key
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  # ── PostgreSQL ────────────────────────────────────────────────
  postgres:
    image: postgres:15-alpine
    container_name: myapp-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data  # persist data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ── Redis ─────────────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    container_name: myapp-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

### Docker Commands

```bash
# ── Build & Run ────────────────────────────────────────────────
docker build -t myapp .                   # build image
docker run -p 8080:8080 myapp             # run container

# ── docker-compose ─────────────────────────────────────────────
docker-compose up                          # start all services
docker-compose up -d                       # start in background
docker-compose up --build                  # rebuild and start
docker-compose down                        # stop all services
docker-compose down -v                     # stop + delete volumes

# ── Logs ───────────────────────────────────────────────────────
docker-compose logs                        # all service logs
docker-compose logs api                    # only API logs
docker-compose logs -f api                 # follow/stream logs

# ── Debug ──────────────────────────────────────────────────────
docker-compose ps                          # show running containers
docker exec -it myapp-api sh               # shell into API container
docker exec -it myapp-postgres psql -U postgres -d myapp  # psql shell
docker exec -it myapp-redis redis-cli      # redis CLI

# ── Cleanup ────────────────────────────────────────────────────
docker system prune                        # remove unused resources
docker image prune                         # remove unused images
```

### Multi-Stage Build Explanation

```dockerfile
# Multi-stage build reduces final image size dramatically

# Stage 1 (builder): golang:1.21 image = ~800MB
# Contains: Go compiler, all build tools
# Only needed during BUILD — not at runtime

# Stage 2 (final): alpine = ~5MB
# Contains: minimal Linux + your binary only
# Final image size: ~15MB instead of ~800MB!

# This matters for:
# - Faster deployment (smaller image to push/pull)
# - Less attack surface (no Go compiler in production)
# - Less storage cost
```

### Health Check Endpoint

```go
// Add to your Go app for Docker health checks
e.GET("/health", func(c echo.Context) error {
    return c.JSON(http.StatusOK, map[string]string{
        "status":  "healthy",
        "version": os.Getenv("APP_VERSION"),
    })
})
```

---

## Interview Questions

### Topics 1–3: Rate Limiting & Redis

**Q: What is rate limiting and why is it important?**
> Rate limiting restricts how many requests a client can make in a given time window. It prevents DDoS attacks, brute force login attempts, API abuse, and ensures fair usage for all clients. A login endpoint might allow 5 requests/minute to prevent password guessing.

**Q: What is Redis and why use it instead of in-memory maps for caching?**
> Redis is an in-memory key-value store. Unlike Go in-memory maps: Redis persists across server restarts, is shared across multiple server instances (horizontal scaling), supports TTL on keys, and has rich data structures (lists, sets, sorted sets). In-memory maps work only for single-instance apps and are lost on restart.

**Q: What is the Cache-Aside (Lazy Loading) pattern?**
> Check cache first. If found (hit), return cached data. If not found (miss), query the database, store the result in cache with a TTL, then return it. This pattern only caches data that is actually requested. Always invalidate cache when underlying data changes.

**Q: What HTTP status code do you return when rate limit is exceeded?**
> 429 Too Many Requests. Also add the `Retry-After` header indicating how many seconds the client should wait before retrying. Add `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers on every response so clients can self-throttle.

### Topics 4–5: Background Jobs & Cron

**Q: Why run tasks in background goroutines instead of in the handler?**
> HTTP handlers should return quickly. Tasks like sending emails, processing images, or generating reports can take seconds — blocking the handler degrades response time. Goroutines let the handler respond immediately while the task runs concurrently. Always log errors from goroutines since the handler won't see them.

**Q: What is a cron expression and give an example?**
> A cron expression specifies when a job runs: `* * * * *` = (minute hour day month weekday). Example: `0 9 * * 1` runs every Monday at 9:00 AM. `*/15 * * * *` runs every 15 minutes. The robfig/cron library also supports seconds as the first field and natural language like `@daily`, `@hourly`, `@every 5m`.

### Topics 6–8: Testing

**Q: What is the difference between unit tests and integration tests?**
> Unit tests test a single function/method in isolation — mock all dependencies (DB, external services). Integration tests test multiple components together — use a real test database. Unit tests are fast (milliseconds), integration tests are slower. Both are needed: unit tests catch logic bugs, integration tests catch wiring bugs.

**Q: What are table-driven tests and why are they preferred in Go?**
> Table-driven tests define test cases as a slice of structs and loop over them. Instead of writing 10 separate test functions, you write one with 10 cases. Benefits: easy to add new cases, all cases visible in one place, DRY (Don't Repeat Yourself), and the `t.Run(name, ...)` subtests show which specific case failed.

**Q: What is httptest and how do you use it?**
> The `net/http/httptest` package provides `httptest.NewRequest()` to create fake HTTP requests and `httptest.NewRecorder()` to capture HTTP responses — all in memory without starting a real server. Used to test HTTP handlers directly. Check `rec.Code` for status and `rec.Body` for response body.

**Q: What does `go test -cover` show?**
> It shows the percentage of code covered by tests. Example: `coverage: 78.3% of statements`. Use `go test -coverprofile=coverage.out ./...` and `go tool cover -html=coverage.out` to see an HTML report highlighting which lines are NOT covered.

### Topic 9: Docker

**Q: What is a multi-stage Docker build and why use it?**
> A multi-stage build uses multiple FROM instructions. Stage 1 (builder) uses the large Go image to compile the binary. Stage 2 (final) uses a tiny Alpine image and copies only the binary. Result: ~15MB image instead of ~800MB. Smaller = faster deploys, less attack surface, lower storage costs.

**Q: Why use `depends_on` with health checks in docker-compose?**
> `depends_on: service` only waits for the container to start, not for the service to be ready. A PostgreSQL container starts in seconds but the DB may take 5-10 seconds to be ready. Adding `condition: service_healthy` with a healthcheck ensures the API doesn't start until PostgreSQL is actually accepting connections.

**Q: What is the difference between `docker build` and `docker-compose up --build`?**
> `docker build` builds a single image from a Dockerfile. `docker-compose up --build` builds all services defined in docker-compose.yml and starts them together with networking and volumes configured. Use `docker-compose` for development — it manages the entire multi-service stack.

---

## Quick Reference Cheatsheet

```go
// ── REDIS ──────────────────────────────────────────────────────
rdb := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
rdb.Ping(ctx)

rdb.Set(ctx, "key", value, 15*time.Minute)
val, err := rdb.Get(ctx, "key").Result()
if err == redis.Nil { /* key not found */ }
rdb.Del(ctx, "key")
rdb.Expire(ctx, "key", 10*time.Minute)
rdb.Incr(ctx, "counter")

// ── CACHE-ASIDE ────────────────────────────────────────────────
func GetUser(id uint) (*User, error) {
    key := fmt.Sprintf("user:%d", id)
    if cached, err := rdb.Get(ctx, key).Result(); err == nil {
        json.Unmarshal([]byte(cached), &user)
        return &user, nil                   // cache HIT
    }
    db.First(&user, id)                     // cache MISS → DB
    data, _ := json.Marshal(user)
    rdb.Set(ctx, key, data, 15*time.Minute) // store in cache
    return &user, nil
}

// ── RATE LIMITER ───────────────────────────────────────────────
count, _ := rdb.Incr(ctx, "rate:"+ip).Result()
if count == 1 { rdb.Expire(ctx, "rate:"+ip, time.Minute) }
if count > limit { return 429 Too Many Requests }

// ── CRON ───────────────────────────────────────────────────────
c := cron.New(cron.WithSeconds())
c.AddFunc("0 0 0 * * *", func() { /* daily midnight */ })
c.AddFunc("@hourly",      func() { /* every hour   */ })
c.AddFunc("@every 5m",    func() { /* every 5 min  */ })
c.Start()
defer c.Stop()

// ── BACKGROUND JOB ────────────────────────────────────────────
go func() {
    if err := doWork(); err != nil {
        log.Printf("background job failed: %v", err)
    }
}()

// ── TESTING ───────────────────────────────────────────────────
func TestFoo(t *testing.T) {
    assert.Equal(t, expected, actual)
    assert.NoError(t, err)
    assert.NotNil(t, result)
    require.NoError(t, err) // stops test on failure
}

// Table-driven
tests := []struct{ name string; input int; want int }{
    {"positive", 5, 25},
    {"zero",     0, 0},
}
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) { assert.Equal(t, tt.want, Square(tt.input)) })
}

// httptest
req := httptest.NewRequest(http.MethodPost, "/users", body)
rec := httptest.NewRecorder()
c   := e.NewContext(req, rec)
handler.CreateUser(c)
assert.Equal(t, 201, rec.Code)

// Run tests
// go test ./...           → all tests
// go test -v ./...        → verbose
// go test -cover ./...    → coverage %
// go test -race ./...     → race detector
```

### Dockerfile Quick Reference

```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
```

```bash
docker-compose up -d          # start all
docker-compose logs -f api    # stream logs
docker-compose down           # stop all
docker exec -it myapp-api sh  # shell into container
```

---

## Resources

- [go-redis GitHub](https://github.com/redis/go-redis)
- [robfig/cron GitHub](https://github.com/robfig/cron)
- [testify GitHub](https://github.com/stretchr/testify)
- [Go testing package](https://pkg.go.dev/testing)
- [Docker official docs](https://docs.docker.com/)
- [docker-compose docs](https://docs.docker.com/compose/)

---

*Phase 2 — Rate Limiting · Redis · Background Jobs · Cron · Testing · Docker — All 9 Topics Covered ✅*