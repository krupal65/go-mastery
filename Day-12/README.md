# 🐹 Go Language — Phase 2 Study Notes

> Complete notes for:
> - **Topic 1: Dockerfile & docker-compose**
> - **Topic 2: PostgreSQL + Go in Docker**
> - **Topic 3: Deploying to AWS EC2**
> - **Topic 4: Reverse Proxy with Nginx**
> - **Topic 5: HTTPS with Let's Encrypt**

---

## 📚 Table of Contents

- [Topic 1: Dockerfile & docker-compose](#topic-1-dockerfile--docker-compose)
- [Topic 2: PostgreSQL + Go in Docker](#topic-2-postgresql--go-in-docker)
- [Topic 3: Deploying to AWS EC2](#topic-3-deploying-to-aws-ec2)
- [Topic 4: Reverse Proxy with Nginx](#topic-4-reverse-proxy-with-nginx)
- [Topic 5: HTTPS with Let's Encrypt](#topic-5-https-with-lets-encrypt)
- [Interview Questions](#interview-questions)
- [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Topic 1: Dockerfile & docker-compose

### What is Docker?

Docker packages your application and all its dependencies into a **container** — a lightweight, isolated environment that runs identically on any machine.

```
Developer's Mac → Docker Container → AWS EC2 → DigitalOcean
Same behavior everywhere — no "works on my machine" problem
```

### Key Docker Concepts

| Concept | Description |
|---|---|
| **Image** | Blueprint/template — built from Dockerfile |
| **Container** | Running instance of an image |
| **Dockerfile** | Instructions to build an image |
| **docker-compose** | Tool to run multi-container apps |
| **Volume** | Persistent storage for containers |
| **Network** | Communication between containers |
| **Registry** | Store and share images (Docker Hub, ECR) |

### Dockerfile — Production-Ready

```dockerfile
# Dockerfile

# ═══════════════════════════════════════════════════
# Stage 1: BUILD — compile the Go binary
# ═══════════════════════════════════════════════════
FROM golang:1.21-alpine AS builder

# Install git (needed for some Go modules)
RUN apk add --no-cache git ca-certificates tzdata

# Set working directory inside container
WORKDIR /app

# Copy dependency files FIRST — Docker caches this layer
# If go.mod/go.sum unchanged, Docker uses cache (faster build)
COPY go.mod go.sum ./
RUN go mod download

# Copy all source code
COPY . .

# Build the binary
# CGO_ENABLED=0  → static binary (no C dependencies)
# GOOS=linux     → compile for Linux (even if building on Mac/Windows)
# -a             → force rebuild all packages
# -o main        → output binary name
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-w -s" \
    -a -installsuffix cgo \
    -o main ./cmd/main.go

# ═══════════════════════════════════════════════════
# Stage 2: RUN — minimal production image
# ═══════════════════════════════════════════════════
FROM alpine:3.18

# Security: run as non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Install runtime dependencies
RUN apk --no-cache add ca-certificates tzdata wget

WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/main .

# Copy any config/migration files if needed
# COPY --from=builder /app/migrations ./migrations

# Set timezone
ENV TZ=Asia/Kolkata

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user (security best practice)
USER appuser

# Expose the port your app listens on
EXPOSE 8080

# Health check — Docker monitors this
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the binary
CMD ["./main"]
```

### .dockerignore

```
# .dockerignore — files excluded from Docker build context
.git
.gitignore
.env
.env.*
!.env.example
*.md
README.md
Dockerfile*
docker-compose*
uploads/
tmp/
*.test
coverage.out
.DS_Store
vendor/
```

### docker-compose.yml — Development

```yaml
# docker-compose.yml — for local development
version: '3.8'

services:

  # ── Go API ──────────────────────────────────────────────────
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: myapp-api
    ports:
      - "8080:8080"
    environment:
      - APP_ENV=development
      - SERVER_PORT=8080
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=secret123
      - DB_NAME=myapp
      - DB_SSLMODE=disable
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET=dev-jwt-secret-change-in-production
    volumes:
      - ./uploads:/app/uploads   # persist uploads
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - myapp-network

  # ── PostgreSQL ───────────────────────────────────────────────
  postgres:
    image: postgres:15-alpine
    container_name: myapp-postgres
    ports:
      - "5432:5432"              # expose for local tools (DBeaver, etc.)
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=secret123
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql  # optional init script
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d myapp"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - myapp-network

  # ── Redis ────────────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    container_name: myapp-redis
    ports:
      - "6379:6379"
    command: redis-server --requirepass redispassword123
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "redispassword123", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - myapp-network

volumes:
  postgres_data:
  redis_data:

networks:
  myapp-network:
    driver: bridge
```

### docker-compose.prod.yml — Production Overrides

```yaml
# docker-compose.prod.yml — extra production settings
version: '3.8'

services:
  api:
    image: myapp:latest          # use pre-built image, not build
    restart: always
    environment:
      - APP_ENV=production
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  postgres:
    ports: []                    # don't expose postgres port in production!
    restart: always

  redis:
    ports: []                    # don't expose redis port in production!
    restart: always
```

### Essential Docker Commands

```bash
# ── Build ──────────────────────────────────────────────────────
docker build -t myapp:latest .          # build image
docker build -t myapp:v1.0.0 .          # with version tag
docker images                            # list images

# ── Run ────────────────────────────────────────────────────────
docker run -p 8080:8080 myapp            # run container
docker run -d -p 8080:8080 myapp         # detached (background)
docker run --env-file .env myapp         # with env file
docker ps                                # list running containers
docker ps -a                             # all containers

# ── docker-compose ─────────────────────────────────────────────
docker-compose up                        # start all services (foreground)
docker-compose up -d                     # start in background
docker-compose up --build                # rebuild + start
docker-compose down                      # stop + remove containers
docker-compose down -v                   # stop + remove volumes too
docker-compose restart api               # restart specific service
docker-compose pull                      # pull latest images

# ── Logs & Debug ───────────────────────────────────────────────
docker-compose logs                      # all logs
docker-compose logs api                  # specific service
docker-compose logs -f api               # follow/stream logs
docker-compose logs --tail=100 api       # last 100 lines

docker exec -it myapp-api sh             # shell into container
docker exec -it myapp-postgres psql -U postgres -d myapp  # psql
docker exec -it myapp-redis redis-cli    # redis cli

docker stats                             # CPU/memory usage
docker inspect myapp-api                 # container details

# ── Cleanup ────────────────────────────────────────────────────
docker stop myapp-api                    # stop container
docker rm myapp-api                      # remove container
docker rmi myapp                         # remove image
docker system prune -a                   # remove everything unused
docker volume prune                      # remove unused volumes
```

---

## Topic 2: PostgreSQL + Go in Docker

### Go App Connecting to PostgreSQL in Docker

The key difference: when running inside Docker, you can't use `localhost` for PostgreSQL. You use the **service name** defined in docker-compose.

```
❌ Outside Docker: DB_HOST=localhost
✅ Inside Docker:  DB_HOST=postgres   (the service name in docker-compose)
```

### Environment Variables Pattern

```go
// config/config.go
package config

import (
    "fmt"
    "os"
    "strconv"
)

type Config struct {
    AppEnv     string
    ServerPort string
    DB         DBConfig
    Redis      RedisConfig
    JWT        JWTConfig
}

type DBConfig struct {
    Host     string
    Port     string
    User     string
    Password string
    Name     string
    SSLMode  string
    MaxOpen  int
    MaxIdle  int
}

func (d DBConfig) DSN() string {
    return fmt.Sprintf(
        "postgresql://%s:%s@%s:%s/%s?sslmode=%s",
        d.User, d.Password, d.Host, d.Port, d.Name, d.SSLMode,
    )
}

func Load() *Config {
    return &Config{
        AppEnv:     getEnv("APP_ENV", "development"),
        ServerPort: getEnv("SERVER_PORT", "8080"),
        DB: DBConfig{
            Host:     getEnv("DB_HOST", "localhost"),
            Port:     getEnv("DB_PORT", "5432"),
            User:     getEnv("DB_USER", "postgres"),
            Password: mustGetEnv("DB_PASSWORD"),
            Name:     getEnv("DB_NAME", "myapp"),
            SSLMode:  getEnv("DB_SSLMODE", "disable"),
            MaxOpen:  getEnvInt("DB_MAX_OPEN_CONNS", 25),
            MaxIdle:  getEnvInt("DB_MAX_IDLE_CONNS", 10),
        },
    }
}

func getEnv(key, def string) string {
    if v := os.Getenv(key); v != "" { return v }
    return def
}

func mustGetEnv(key string) string {
    v := os.Getenv(key)
    if v == "" { panic("required env var not set: " + key) }
    return v
}

func getEnvInt(key string, def int) int {
    if v := os.Getenv(key); v != "" {
        if i, err := strconv.Atoi(v); err == nil { return i }
    }
    return def
}
```

### Database Connection with Retry

```go
// database/connect.go
package database

import (
    "fmt"
    "log"
    "time"

    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

func Connect(dsn string, maxOpen, maxIdle int) (*gorm.DB, error) {
    var db *gorm.DB
    var err error

    // Retry connection — important for Docker startup order
    // PostgreSQL might not be ready when API container starts
    maxRetries := 10
    for i := 0; i < maxRetries; i++ {
        db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
            Logger: logger.Default.LogMode(logger.Warn),
        })
        if err == nil {
            break
        }
        log.Printf("DB connection attempt %d/%d failed: %v", i+1, maxRetries, err)
        time.Sleep(3 * time.Second)   // wait 3 seconds before retry
    }

    if err != nil {
        return nil, fmt.Errorf("failed to connect after %d attempts: %w", maxRetries, err)
    }

    // Configure connection pool
    sqlDB, err := db.DB()
    if err != nil {
        return nil, err
    }
    sqlDB.SetMaxOpenConns(maxOpen)
    sqlDB.SetMaxIdleConns(maxIdle)
    sqlDB.SetConnMaxLifetime(5 * time.Minute)
    sqlDB.SetConnMaxIdleTime(2 * time.Minute)

    log.Println("✅ Database connected successfully")
    return db, nil
}
```

### Docker Init SQL (Optional)

```sql
-- scripts/init.sql
-- Runs when PostgreSQL container starts for the first time

-- Create additional databases
CREATE DATABASE myapp_test;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for ILIKE performance

-- Create initial admin user (optional)
-- (your Go app should handle migrations and seeding)
```

### Running Migrations in Docker

```go
// cmd/migrate/main.go — separate migration binary
package main

import (
    "log"
    "github.com/joho/godotenv"
    "myapp/config"
    "myapp/database"
    "myapp/models"
)

func main() {
    godotenv.Load()
    cfg := config.Load()

    db, err := database.Connect(cfg.DB.DSN(), 5, 2)
    if err != nil {
        log.Fatal("DB connection failed:", err)
    }

    log.Println("Running migrations...")
    err = db.AutoMigrate(
        &models.User{},
        &models.Product{},
        &models.Order{},
    )
    if err != nil {
        log.Fatal("Migration failed:", err)
    }

    log.Println("✅ Migrations completed!")
}
```

```yaml
# docker-compose with migration service
services:
  migrate:
    build: .
    command: ["./migrate"]       # run migration binary
    environment:
      - DB_HOST=postgres
      - DB_PASSWORD=secret123
    depends_on:
      postgres:
        condition: service_healthy
    restart: on-failure          # retry if DB not ready

  api:
    depends_on:
      migrate:
        condition: service_completed_successfully
```

---

## Topic 3: Deploying to AWS EC2

### What is AWS EC2?

EC2 (Elastic Compute Cloud) is a virtual server in Amazon's data center. You rent a machine, SSH into it, and run your app.

```
Your Laptop → (SSH) → EC2 Instance → Internet
                      ├── Your Go App
                      ├── PostgreSQL (or RDS)
                      ├── Redis
                      └── Nginx (reverse proxy)
```

### Step 1 — Launch EC2 Instance

```
AWS Console → EC2 → Launch Instance

Recommended settings:
  AMI:            Ubuntu 22.04 LTS (free tier eligible)
  Instance type:  t2.micro (free tier) or t3.small for production
  Storage:        20 GB gp3 SSD
  Security Group: Allow inbound
                  - SSH (22) from your IP only
                  - HTTP (80) from anywhere
                  - HTTPS (443) from anywhere
  Key pair:       Create new → download .pem file (KEEP SAFE!)
```

### Step 2 — Connect to EC2

```bash
# Fix key file permissions (required on Mac/Linux)
chmod 400 ~/Downloads/myapp-key.pem

# Connect via SSH
ssh -i ~/Downloads/myapp-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Example
ssh -i myapp-key.pem ubuntu@54.210.123.45
```

### Step 3 — Setup EC2 Server

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add ubuntu user to docker group (no sudo needed)
sudo usermod -aG docker ubuntu
newgrp docker   # apply group change immediately

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify installations
docker --version
docker compose version
```

### Step 4 — Deploy Your App

```bash
# ── Method 1: Clone from Git ───────────────────────────────────
git clone https://github.com/yourusername/myapp.git
cd myapp

# Create .env file with production values
nano .env

# Start app
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# ── Method 2: Pull from Docker Hub ────────────────────────────
# On your local machine:
docker build -t yourusername/myapp:latest .
docker push yourusername/myapp:latest

# On EC2:
docker pull yourusername/myapp:latest
docker compose up -d
```

### Step 5 — Production .env on EC2

```bash
# Create production .env — never commit this!
cat > .env << 'EOF'
APP_ENV=production
SERVER_PORT=8080

DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=CHANGE_TO_STRONG_PASSWORD_HERE
DB_NAME=myapp
DB_SSLMODE=disable

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=CHANGE_TO_STRONG_REDIS_PASSWORD

JWT_SECRET=CHANGE_TO_64_CHAR_RANDOM_STRING
JWT_EXPIRE_HOURS=24

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=yourapp@gmail.com
SMTP_PASSWORD=your_gmail_app_password
EOF

# Set proper permissions — only owner can read
chmod 600 .env
```

### Step 6 — Basic Server Maintenance

```bash
# Check running containers
docker compose ps

# View logs
docker compose logs -f api
docker compose logs --tail=100 postgres

# Restart a service
docker compose restart api

# Update and redeploy
git pull origin main
docker compose up --build -d

# Stop everything
docker compose down

# Check disk usage
df -h
docker system df

# Check memory/CPU
free -h
top
```

### EC2 Security Best Practices

```bash
# ── Firewall with UFW ──────────────────────────────────────────
sudo ufw enable
sudo ufw allow 22/tcp       # SSH
sudo ufw allow 80/tcp       # HTTP
sudo ufw allow 443/tcp      # HTTPS
sudo ufw deny 5432/tcp      # Block direct DB access from internet
sudo ufw deny 6379/tcp      # Block direct Redis access
sudo ufw status

# ── Automatic security updates ─────────────────────────────────
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure unattended-upgrades

# ── Fail2ban — blocks repeated failed SSH logins ───────────────
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Topic 4: Reverse Proxy with Nginx

### What is a Reverse Proxy?

A reverse proxy sits in front of your app server and forwards client requests to it.

```
Internet → Nginx (port 80/443) → Go App (port 8080)

Without Nginx:  client → :8080 (Go app directly)
With Nginx:     client → :80/:443 (Nginx) → :8080 (Go app)
```

**Why use Nginx as a reverse proxy?**
- Handles SSL/TLS (HTTPS) — Go app only deals with HTTP
- Serves static files (faster than Go)
- Load balancing across multiple app instances
- Rate limiting at the network level
- Compression (gzip)
- Request buffering — protects slow backend
- Better logging

### Install Nginx on EC2

```bash
# Install Nginx
sudo apt install nginx -y

# Start and enable on boot
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx

# Test config (before applying changes)
sudo nginx -t
```

### Nginx Configuration for Go API

```nginx
# /etc/nginx/sites-available/myapp
# This file configures Nginx for your Go application

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # ── Logging ─────────────────────────────────────────────────
    access_log /var/log/nginx/myapp_access.log;
    error_log  /var/log/nginx/myapp_error.log;

    # ── Security headers ─────────────────────────────────────────
    add_header X-Content-Type-Options    nosniff;
    add_header X-Frame-Options           DENY;
    add_header X-XSS-Protection          "1; mode=block";
    add_header Referrer-Policy           strict-origin-when-cross-origin;

    # ── File upload size limit ───────────────────────────────────
    client_max_body_size 20M;

    # ── Gzip compression ─────────────────────────────────────────
    gzip on;
    gzip_types application/json text/plain text/css application/javascript;
    gzip_min_length 1024;

    # ── Proxy API requests to Go app ─────────────────────────────
    location /api/ {
        proxy_pass         http://localhost:8080;
        proxy_http_version 1.1;

        # Pass client info to Go app
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout    60s;
        proxy_read_timeout    60s;
    }

    # ── Health check endpoint ────────────────────────────────────
    location /health {
        proxy_pass http://localhost:8080;
    }

    # ── Serve static/uploaded files directly (faster) ───────────
    location /uploads/ {
        root /app;                          # serves /app/uploads/...
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # ── Block common attack patterns ─────────────────────────────
    location ~ /\. {
        deny all;                           # block .env, .git etc.
    }
}
```

### Enable the Configuration

```bash
# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/

# Remove default Nginx site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx (no downtime)
sudo systemctl reload nginx

# Restart Nginx (brief downtime)
sudo systemctl restart nginx
```

### Get Real Client IP in Go App

```go
// When behind Nginx, c.RealIP() reads X-Real-IP header
// But you must configure Echo to trust the proxy

func main() {
    e := echo.New()

    // Tell Echo it's behind a trusted proxy
    e.IPExtractor = echo.ExtractIPFromXFFHeader()
    // OR
    e.IPExtractor = echo.ExtractIPFromRealIPHeader()

    // Now c.RealIP() returns the actual client IP, not Nginx's IP
}
```

---

## Topic 5: HTTPS with Let's Encrypt

### What is HTTPS and Let's Encrypt?

**HTTPS** encrypts communication between client and server using TLS. Without it, passwords and tokens are visible to anyone on the network.

**Let's Encrypt** is a free, automated Certificate Authority (CA) that issues SSL/TLS certificates. You need:
- A domain name (yourdomain.com) pointing to your EC2 IP
- Port 80 and 443 open

### Step 1 — Point Domain to EC2

```
In your domain registrar (GoDaddy, Namecheap, etc.):

Add DNS A Records:
  Type: A    Name: @              Value: YOUR_EC2_IP  TTL: 300
  Type: A    Name: www            Value: YOUR_EC2_IP  TTL: 300
  Type: A    Name: api            Value: YOUR_EC2_IP  TTL: 300

Wait 5-60 minutes for DNS to propagate
Verify: nslookup yourdomain.com  →  should return EC2 IP
```

### Step 2 — Install Certbot

```bash
# Install Certbot (Let's Encrypt client)
sudo apt install certbot python3-certbot-nginx -y
```

### Step 3 — Get SSL Certificate

```bash
# Certbot automatically:
# 1. Verifies you own the domain
# 2. Issues certificate
# 3. Configures Nginx for HTTPS
# 4. Sets up auto-renewal

sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email for renewal notifications
# - Agree to terms of service
# - Choose redirect option (2 — redirect HTTP to HTTPS)
```

### What Certbot Adds to Nginx Config

```nginx
# Certbot automatically modifies your Nginx config:

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    # Certbot adds this:
    return 301 https://$host$request_uri;  # redirect HTTP → HTTPS
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    # ── SSL certificates (added by Certbot) ──────────────────
    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    # ── Your existing config remains ──────────────────────────
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    # ... rest of config ...
}
```

### Step 4 — Auto-Renewal

```bash
# Let's Encrypt certificates expire every 90 days
# Certbot sets up auto-renewal via cron/systemd automatically

# Verify auto-renewal is scheduled
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status snap.certbot.renew.timer
# OR
sudo crontab -l | grep certbot

# Manual renewal
sudo certbot renew

# After renewal, reload Nginx
sudo systemctl reload nginx
```

### Complete Nginx HTTPS Config

```nginx
# /etc/nginx/sites-available/myapp
# Full production config with HTTPS

# ── Redirect HTTP to HTTPS ────────────────────────────────────
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

# ── HTTPS Server ─────────────────────────────────────────────
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # ── SSL ──────────────────────────────────────────────────
    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    # ── HSTS — tells browsers to always use HTTPS ─────────────
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # ── Security headers ──────────────────────────────────────
    add_header X-Content-Type-Options    nosniff         always;
    add_header X-Frame-Options           DENY            always;
    add_header X-XSS-Protection          "1; mode=block" always;
    add_header Referrer-Policy           strict-origin-when-cross-origin always;

    # ── Limits ───────────────────────────────────────────────
    client_max_body_size 20M;

    # ── Gzip ─────────────────────────────────────────────────
    gzip on;
    gzip_vary on;
    gzip_types application/json text/plain text/css application/javascript image/svg+xml;
    gzip_min_length 1024;

    # ── API ──────────────────────────────────────────────────
    location /api/ {
        proxy_pass         http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto https;
        proxy_set_header   Upgrade           $http_upgrade;
        proxy_set_header   Connection        "upgrade";
        proxy_connect_timeout 60s;
        proxy_read_timeout    60s;
    }

    location /health {
        proxy_pass http://localhost:8080;
    }

    # ── Static/Uploaded files ─────────────────────────────────
    location /uploads/ {
        root   /app;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # ── Block hidden files ────────────────────────────────────
    location ~ /\. {
        deny all;
    }
}
```

### Complete Deployment Flow — Summary

```
┌─────────────────────────────────────────────┐
│           COMPLETE DEPLOYMENT FLOW           │
├─────────────────────────────────────────────┤
│                                              │
│  1. Write Go code + Dockerfile               │
│     └── docker-compose.yml                  │
│                                              │
│  2. Launch EC2 (Ubuntu 22.04)                │
│     └── Open ports 22, 80, 443              │
│                                              │
│  3. SSH into EC2                             │
│     └── sudo apt update                     │
│     └── Install Docker + Compose            │
│                                              │
│  4. Clone repo + create .env                 │
│     └── docker compose up -d                │
│     └── Go app running on :8080             │
│                                              │
│  5. Install + configure Nginx                │
│     └── /api/ → localhost:8080              │
│     └── Test: http://yourdomain.com/api/... │
│                                              │
│  6. Point domain to EC2 IP (DNS A record)    │
│                                              │
│  7. Install Certbot + get certificate        │
│     └── sudo certbot --nginx -d domain.com  │
│     └── HTTPS enabled automatically!        │
│                                              │
│  8. Verify:                                  │
│     └── https://yourdomain.com/api/health   │
│     └── https + green lock ✅               │
│                                              │
└─────────────────────────────────────────────┘
```

---

## Interview Questions

### Topic 1–2: Dockerfile & Docker Compose

**Q: What is a multi-stage Dockerfile and why use it?**
> A multi-stage build uses multiple FROM instructions. Stage 1 (builder) uses the large Go image (~800MB) to compile the binary. Stage 2 (final) uses tiny Alpine (~5MB) and copies only the compiled binary. Result: ~15MB image. Benefits: faster deploys, less storage cost, smaller attack surface (no Go compiler or build tools in production).

**Q: Why copy go.mod and go.sum before source code in Dockerfile?**
> Docker caches layers. If go.mod and go.sum haven't changed, Docker reuses the cached `go mod download` layer — skipping a slow download step. If you copy all source first, any code change would invalidate the dependency cache. This ordering makes rebuilds much faster.

**Q: What is the difference between docker build and docker-compose up?**
> `docker build` builds a single image from a Dockerfile. `docker-compose up` reads docker-compose.yml, builds/pulls all service images, creates a network, mounts volumes, and starts all containers in the correct order with `depends_on`. Use docker-compose to manage a multi-service stack.

**Q: Why should you not expose database ports (5432, 6379) in production?**
> Exposing DB ports lets anyone on the internet attempt to connect and brute-force credentials. In production, only the API container needs to talk to the database — and they communicate via Docker's internal network. Never expose DB ports publicly; use UFW/security groups to block them.

**Q: How do containers communicate with each other in docker-compose?**
> docker-compose creates a shared network for all services. Containers reach each other by **service name** — not localhost or IP. If your DB service is named `postgres`, the API connects to `DB_HOST=postgres`. Docker's DNS resolves the service name to the container's internal IP automatically.

### Topic 3: AWS EC2

**Q: What is the deployment workflow for a Go app on EC2?**
> Launch EC2 instance → SSH in → Install Docker and docker-compose → Clone repo → Create production .env → Run `docker compose up -d` → Install and configure Nginx → Point domain DNS to EC2 IP → Install Certbot for HTTPS. The app is then accessible at https://yourdomain.com.

**Q: Why should you use `chmod 400` on your .pem key file?**
> SSH refuses to use a private key that is readable by others (group/world). `chmod 400` makes it readable only by the owner. This is a security requirement — SSH will refuse connection with "WARNING: UNPROTECTED PRIVATE KEY FILE!" if permissions are too open.

### Topic 4: Nginx

**Q: What is a reverse proxy and why use Nginx in front of Go?**
> A reverse proxy accepts client requests and forwards them to a backend server. Nginx in front of Go handles SSL termination (Go only deals with plain HTTP internally), serves static files faster, provides rate limiting, gzip compression, request buffering, and better logging. It also lets you run multiple services on one server.

**Q: What Nginx headers should you forward to the Go app?**
> `X-Real-IP` — actual client IP. `X-Forwarded-For` — chain of proxies. `X-Forwarded-Proto` — original protocol (https). `Host` — original domain name. Without these, your Go app thinks all requests come from localhost and sees only HTTP even when the client used HTTPS.

**Q: What does `proxy_set_header X-Forwarded-Proto $scheme` do?**
> It tells the Go app whether the original request was HTTP or HTTPS. Without it, your app always sees HTTP (because Nginx talks to Go over HTTP internally). This is important for generating correct URLs and for security checks that require HTTPS.

### Topic 5: HTTPS & Let's Encrypt

**Q: What is Let's Encrypt and how does certificate renewal work?**
> Let's Encrypt is a free CA that issues 90-day SSL certificates. Certbot automates the entire process: domain verification, certificate issuance, Nginx config update, and renewal. It installs a cron job that attempts renewal every 12 hours, renewing when the cert has less than 30 days left.

**Q: What is HSTS and why is it important?**
> HSTS (HTTP Strict Transport Security) tells browsers to always use HTTPS for your domain — even if the user types http://. The `Strict-Transport-Security` header with `max-age=31536000` makes browsers remember this for 1 year. Prevents SSL stripping attacks where an attacker downgrades to HTTP.

**Q: What is the difference between ssl_certificate and ssl_certificate_key?**
> `ssl_certificate` is the public certificate (and chain) that gets sent to clients — proves your server's identity. `ssl_certificate_key` is the private key — kept secret on the server, used to decrypt data encrypted with your public key. Never share or expose the private key.

---

## Quick Reference Cheatsheet

```dockerfile
# ── DOCKERFILE ─────────────────────────────────────────────────
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./cmd/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
```

```yaml
# ── DOCKER-COMPOSE ─────────────────────────────────────────────
services:
  api:
    build: .
    ports: ["8080:8080"]
    depends_on:
      postgres: { condition: service_healthy }
  postgres:
    image: postgres:15-alpine
    environment: { POSTGRES_PASSWORD: secret }
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s; retries: 5
volumes:
  postgres_data:
```

```bash
# ── DOCKER COMMANDS ────────────────────────────────────────────
docker-compose up -d          # start all in background
docker-compose up --build -d  # rebuild and start
docker-compose logs -f api    # stream logs
docker-compose down           # stop all
docker exec -it myapp-api sh  # shell into container

# ── EC2 SETUP ──────────────────────────────────────────────────
chmod 400 key.pem
ssh -i key.pem ubuntu@EC2_IP
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu

# ── NGINX ──────────────────────────────────────────────────────
sudo apt install nginx -y
# edit /etc/nginx/sites-available/myapp
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t            # test config
sudo systemctl reload nginx

# Nginx proxy config:
# location /api/ {
#   proxy_pass http://localhost:8080;
#   proxy_set_header Host $host;
#   proxy_set_header X-Real-IP $remote_addr;
#   proxy_set_header X-Forwarded-Proto $scheme;
# }

# ── HTTPS CERTBOT ──────────────────────────────────────────────
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo certbot renew --dry-run  # test auto-renewal

# ── SECURITY ───────────────────────────────────────────────────
sudo ufw allow 22/tcp; sudo ufw allow 80/tcp; sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp; sudo ufw deny 6379/tcp
sudo ufw enable
```

---

## Resources

- [Docker Official Docs](https://docs.docker.com/)
- [docker-compose Reference](https://docs.docker.com/compose/compose-file/)
- [AWS EC2 User Guide](https://docs.aws.amazon.com/ec2/index.html)
- [Nginx Docs](https://nginx.org/en/docs/)
- [Certbot Docs](https://certbot.eff.org/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

*Phase 2 — Dockerfile · docker-compose · EC2 · Nginx · HTTPS — All 5 Topics Covered ✅*
*Phase 2 Completely Done! 🎉*