# 🐹 Go Language — Phase 2 Study Notes

> Complete notes for:
> - **Topic 1: File Upload & Static Serving**
> - **Topic 2: Upload Images/Docs**
> - **Topic 3: Serve Static Files**
> - **Topic 4: Pagination, Filtering, and Sorting**
> - **Topic 5: SQL Pagination**
> - **Topic 6: API Query Parameters**

---

## 📚 Table of Contents

- [Topic 1: File Upload & Static Serving](#topic-1-file-upload--static-serving)
- [Topic 2: Upload Images/Docs](#topic-2-upload-imagesdocs)
- [Topic 3: Serve Static Files](#topic-3-serve-static-files)
- [Topic 4: Pagination, Filtering, and Sorting](#topic-4-pagination-filtering-and-sorting)
- [Topic 5: SQL Pagination](#topic-5-sql-pagination)
- [Topic 6: API Query Parameters](#topic-6-api-query-parameters)
- [Interview Questions](#interview-questions)
- [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Topic 1: File Upload & Static Serving

### What is File Upload?

File upload lets clients send binary files (images, PDFs, documents) to the server via HTTP. The standard format is `multipart/form-data`.

### How multipart/form-data Works

```
POST /upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----FormBoundary

------FormBoundary
Content-Disposition: form-data; name="file"; filename="photo.jpg"
Content-Type: image/jpeg

<binary file data here>
------FormBoundary--
```

### Project Structure for File Handling

```
myapp/
├── main.go
├── handlers/
│   └── upload.go
├── uploads/              ← uploaded files saved here
│   ├── images/
│   └── docs/
└── static/               ← static files served directly
    ├── css/
    ├── js/
    └── images/
```

### Echo File Upload Setup

```go
package main

import (
    "github.com/labstack/echo/v4"
)

func main() {
    e := echo.New()

    // Set max file size for multipart forms (default 32MB)
    e.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
        return func(c echo.Context) error {
            c.Request().Body = http.MaxBytesReader(
                c.Response().Writer,
                c.Request().Body,
                10<<20, // 10 MB limit
            )
            return next(c)
        }
    })

    // Upload routes
    e.POST("/upload/image",    uploadImage)
    e.POST("/upload/document", uploadDocument)
    e.POST("/upload/multiple", uploadMultiple)

    // Serve static files
    e.Static("/static", "static")    // /static/img.jpg → ./static/img.jpg
    e.Static("/uploads", "uploads")  // /uploads/abc.jpg → ./uploads/abc.jpg

    e.Logger.Fatal(e.Start(":8080"))
}
```

---

## Topic 2: Upload Images/Docs

### Single File Upload

```go
// handlers/upload.go
package handlers

import (
    "fmt"
    "io"
    "net/http"
    "os"
    "path/filepath"
    "strings"
    "time"

    "github.com/labstack/echo/v4"
)

type UploadResponse struct {
    FileName    string `json:"file_name"`
    OriginalName string `json:"original_name"`
    Size        int64  `json:"size"`
    URL         string `json:"url"`
    ContentType string `json:"content_type"`
}

func UploadImage(c echo.Context) error {
    // ── Step 1: Get file from form ────────────────────────────
    // "file" is the form field name — must match client's field name
    file, err := c.FormFile("file")
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "file is required (field name: 'file')",
        })
    }

    // ── Step 2: Validate file type ────────────────────────────
    allowedTypes := map[string]bool{
        "image/jpeg": true,
        "image/png":  true,
        "image/gif":  true,
        "image/webp": true,
    }
    contentType := file.Header.Get("Content-Type")
    if !allowedTypes[contentType] {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "only JPEG, PNG, GIF and WebP images are allowed",
        })
    }

    // ── Step 3: Validate file size (5MB max) ──────────────────
    const maxSize = 5 * 1024 * 1024  // 5 MB
    if file.Size > maxSize {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "file size must not exceed 5MB",
        })
    }

    // ── Step 4: Generate unique filename ──────────────────────
    ext := filepath.Ext(file.Filename)                          // .jpg
    newFileName := fmt.Sprintf("%d%s", time.Now().UnixNano(), ext)  // unique name
    uploadPath := filepath.Join("uploads", "images", newFileName)

    // ── Step 5: Create upload directory if not exists ─────────
    if err := os.MkdirAll(filepath.Dir(uploadPath), 0755); err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not create upload directory",
        })
    }

    // ── Step 6: Open uploaded file ────────────────────────────
    src, err := file.Open()
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not open uploaded file",
        })
    }
    defer src.Close()

    // ── Step 7: Create destination file ──────────────────────
    dst, err := os.Create(uploadPath)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not save file",
        })
    }
    defer dst.Close()

    // ── Step 8: Copy file contents ────────────────────────────
    if _, err := io.Copy(dst, src); err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not write file",
        })
    }

    // ── Step 9: Return response ───────────────────────────────
    fileURL := fmt.Sprintf("/uploads/images/%s", newFileName)
    return c.JSON(http.StatusCreated, UploadResponse{
        FileName:     newFileName,
        OriginalName: file.Filename,
        Size:         file.Size,
        URL:          fileURL,
        ContentType:  contentType,
    })
}
```

### Document Upload

```go
func UploadDocument(c echo.Context) error {
    file, err := c.FormFile("document")
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "document field is required",
        })
    }

    // ── Validate document types ───────────────────────────────
    allowedExtensions := map[string]bool{
        ".pdf":  true,
        ".doc":  true,
        ".docx": true,
        ".txt":  true,
        ".xlsx": true,
        ".csv":  true,
    }

    ext := strings.ToLower(filepath.Ext(file.Filename))
    if !allowedExtensions[ext] {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "allowed types: PDF, DOC, DOCX, TXT, XLSX, CSV",
        })
    }

    // ── Validate size (10MB for docs) ─────────────────────────
    const maxSize = 10 * 1024 * 1024 // 10 MB
    if file.Size > maxSize {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "document must not exceed 10MB",
        })
    }

    // ── Save file ─────────────────────────────────────────────
    newFileName := fmt.Sprintf("%d_%s", time.Now().UnixNano(), file.Filename)
    uploadPath  := filepath.Join("uploads", "docs", newFileName)
    os.MkdirAll(filepath.Dir(uploadPath), 0755)

    src, _ := file.Open()
    defer src.Close()

    dst, err := os.Create(uploadPath)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not save document",
        })
    }
    defer dst.Close()
    io.Copy(dst, src)

    return c.JSON(http.StatusCreated, UploadResponse{
        FileName:     newFileName,
        OriginalName: file.Filename,
        Size:         file.Size,
        URL:          fmt.Sprintf("/uploads/docs/%s", newFileName),
    })
}
```

### Multiple File Upload

```go
func UploadMultiple(c echo.Context) error {
    // Parse multipart form — must call this before MultipartForm
    form, err := c.MultipartForm()
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid multipart form",
        })
    }

    // Get all files from "files" field
    files := form.File["files"]
    if len(files) == 0 {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "at least one file is required",
        })
    }

    // Limit number of files
    if len(files) > 10 {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "maximum 10 files allowed",
        })
    }

    var uploaded []UploadResponse

    for _, file := range files {
        // Validate each file
        if file.Size > 5*1024*1024 {
            return c.JSON(http.StatusBadRequest, map[string]string{
                "error": fmt.Sprintf("file %s exceeds 5MB limit", file.Filename),
            })
        }

        // Save each file
        ext         := filepath.Ext(file.Filename)
        newFileName := fmt.Sprintf("%d%s", time.Now().UnixNano(), ext)
        uploadPath  := filepath.Join("uploads", "images", newFileName)
        os.MkdirAll(filepath.Dir(uploadPath), 0755)

        src, _  := file.Open()
        dst, _  := os.Create(uploadPath)
        io.Copy(dst, src)
        src.Close()
        dst.Close()

        uploaded = append(uploaded, UploadResponse{
            FileName:     newFileName,
            OriginalName: file.Filename,
            Size:         file.Size,
            URL:          fmt.Sprintf("/uploads/images/%s", newFileName),
        })
    }

    return c.JSON(http.StatusCreated, map[string]interface{}{
        "message": fmt.Sprintf("%d files uploaded", len(uploaded)),
        "files":   uploaded,
    })
}
```

### Upload with Form Fields (Mixed Data + File)

```go
// Upload image AND save product info in one request
func CreateProductWithImage(c echo.Context) error {
    // ── Read form fields ──────────────────────────────────────
    name        := c.FormValue("name")
    priceStr    := c.FormValue("price")
    description := c.FormValue("description")

    price, err := strconv.ParseFloat(priceStr, 64)
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "price must be a number",
        })
    }

    // ── Read file ─────────────────────────────────────────────
    file, err := c.FormFile("image")
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "product image is required",
        })
    }

    // Save image (same as above)...
    imageURL := saveFile(file, "uploads/products")

    // ── Save to database ──────────────────────────────────────
    product := models.Product{
        Name:        name,
        Price:       price,
        Description: description,
        ImageURL:    imageURL,
    }
    h.db.Create(&product)

    return c.JSON(http.StatusCreated, product)
}
```

### File Validation Helper

```go
// helpers/file.go
package helpers

import (
    "fmt"
    "mime/multipart"
    "path/filepath"
    "strings"
)

type FileValidator struct {
    MaxSize      int64
    AllowedTypes []string
    AllowedExts  []string
}

var ImageValidator = FileValidator{
    MaxSize:      5 * 1024 * 1024,  // 5MB
    AllowedTypes: []string{"image/jpeg", "image/png", "image/gif", "image/webp"},
    AllowedExts:  []string{".jpg", ".jpeg", ".png", ".gif", ".webp"},
}

var DocumentValidator = FileValidator{
    MaxSize:     20 * 1024 * 1024, // 20MB
    AllowedExts: []string{".pdf", ".doc", ".docx", ".txt", ".xlsx", ".csv"},
}

func (v FileValidator) Validate(file *multipart.FileHeader) error {
    // Check size
    if file.Size > v.MaxSize {
        return fmt.Errorf("file too large: max %dMB", v.MaxSize/(1024*1024))
    }

    // Check extension
    if len(v.AllowedExts) > 0 {
        ext := strings.ToLower(filepath.Ext(file.Filename))
        allowed := false
        for _, e := range v.AllowedExts {
            if ext == e { allowed = true; break }
        }
        if !allowed {
            return fmt.Errorf("file type not allowed: %s", ext)
        }
    }

    // Check content type
    if len(v.AllowedTypes) > 0 {
        ct := file.Header.Get("Content-Type")
        allowed := false
        for _, t := range v.AllowedTypes {
            if ct == t { allowed = true; break }
        }
        if !allowed {
            return fmt.Errorf("content type not allowed: %s", ct)
        }
    }

    return nil
}

// Usage
if err := helpers.ImageValidator.Validate(file); err != nil {
    return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
}
```

---

## Topic 3: Serve Static Files

### Serving Static Files with Echo

```go
func main() {
    e := echo.New()

    // ── Serve entire directory ────────────────────────────────
    // URL prefix → local directory
    e.Static("/static",  "static")   // GET /static/css/app.css → ./static/css/app.css
    e.Static("/uploads", "uploads")  // GET /uploads/img.jpg   → ./uploads/img.jpg

    // ── Serve single file ─────────────────────────────────────
    e.File("/favicon.ico",   "static/favicon.ico")
    e.File("/robots.txt",    "static/robots.txt")
    e.File("/",              "static/index.html")  // SPA root

    // ── Serve SPA (Single Page App) ───────────────────────────
    // All unmatched routes → index.html (for React/Vue router)
    e.GET("/*", func(c echo.Context) error {
        return c.File("static/index.html")
    })

    e.Logger.Fatal(e.Start(":8080"))
}
```

### Serve Files with Custom Headers

```go
// Add cache headers for static files
func staticWithCache(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        path := c.Request().URL.Path

        // Cache images for 1 year
        if strings.HasPrefix(path, "/uploads/") ||
           strings.HasPrefix(path, "/static/images/") {
            c.Response().Header().Set("Cache-Control", "public, max-age=31536000")
        }

        // Cache CSS/JS for 1 week
        if strings.HasSuffix(path, ".css") || strings.HasSuffix(path, ".js") {
            c.Response().Header().Set("Cache-Control", "public, max-age=604800")
        }

        return next(c)
    }
}

e.Use(staticWithCache)
e.Static("/static", "static")
```

### Download File (Force Download)

```go
// Force browser to download instead of display
func DownloadFile(c echo.Context) error {
    filename := c.Param("filename")

    // Security — prevent path traversal attack!
    // Never allow ../ in filename
    if strings.Contains(filename, "..") || strings.Contains(filename, "/") {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid filename",
        })
    }

    filePath := filepath.Join("uploads", "docs", filename)

    // Check file exists
    if _, err := os.Stat(filePath); os.IsNotExist(err) {
        return c.JSON(http.StatusNotFound, map[string]string{
            "error": "file not found",
        })
    }

    // Set headers to force download
    c.Response().Header().Set("Content-Disposition",
        fmt.Sprintf(`attachment; filename="%s"`, filename))

    return c.File(filePath)
}

// Route
e.GET("/download/:filename", DownloadFile)
```

### Delete File

```go
func DeleteFile(c echo.Context) error {
    filename := c.Param("filename")

    // Security check
    if strings.Contains(filename, "..") {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid filename",
        })
    }

    filePath := filepath.Join("uploads", filename)

    if err := os.Remove(filePath); err != nil {
        if os.IsNotExist(err) {
            return c.JSON(http.StatusNotFound, map[string]string{
                "error": "file not found",
            })
        }
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not delete file",
        })
    }

    return c.JSON(http.StatusOK, map[string]string{
        "message": "file deleted successfully",
    })
}
```

---

## Topic 4: Pagination, Filtering, and Sorting

### Why Pagination?

Without pagination, a `GET /users` endpoint could return millions of records — crashing the server and the client. Pagination splits results into pages.

### Pagination Concepts

```
Total records: 1000
Page size (limit): 10
Total pages: 1000 / 10 = 100

Page 1: records 1–10    offset=0
Page 2: records 11–20   offset=10
Page 3: records 21–30   offset=20
Page N: offset = (page - 1) * limit
```

### Pagination Request & Response

```go
// Request — what the client sends as query params
type PaginationRequest struct {
    Page  int `query:"page"`   // default: 1
    Limit int `query:"limit"`  // default: 10, max: 100
}

func (p *PaginationRequest) SetDefaults() {
    if p.Page  <= 0 { p.Page  = 1   }
    if p.Limit <= 0 { p.Limit = 10  }
    if p.Limit > 100 { p.Limit = 100 } // prevent abuse
}

func (p *PaginationRequest) Offset() int {
    return (p.Page - 1) * p.Limit
}

// Response — what the server returns
type PaginatedResponse struct {
    Data       interface{} `json:"data"`
    Page       int         `json:"page"`
    Limit      int         `json:"limit"`
    Total      int64       `json:"total"`       // total matching records
    TotalPages int         `json:"total_pages"`
    HasNext    bool        `json:"has_next"`
    HasPrev    bool        `json:"has_prev"`
}

func NewPaginatedResponse(data interface{}, page, limit int, total int64) PaginatedResponse {
    totalPages := int(math.Ceil(float64(total) / float64(limit)))
    return PaginatedResponse{
        Data:       data,
        Page:       page,
        Limit:      limit,
        Total:      total,
        TotalPages: totalPages,
        HasNext:    page < totalPages,
        HasPrev:    page > 1,
    }
}
```

### Filtering

```go
// Filter request — all fields optional
type UserFilterRequest struct {
    Name     string `query:"name"`      // search by name (LIKE)
    Email    string `query:"email"`     // exact match
    Role     string `query:"role"`      // exact match
    IsActive *bool  `query:"is_active"` // pointer — distinguish false from not-set
    AgeMin   int    `query:"age_min"`
    AgeMax   int    `query:"age_max"`
}
```

### Sorting

```go
// Sorting request
type SortRequest struct {
    SortBy    string `query:"sort_by"`    // field name: name, email, created_at
    SortOrder string `query:"sort_order"` // asc or desc
}

func (s *SortRequest) SetDefaults() {
    if s.SortBy    == "" { s.SortBy    = "created_at" }
    if s.SortOrder == "" { s.SortOrder = "desc"       }
}

// Security — only allow sorting on known safe columns (prevent SQL injection)
func (s *SortRequest) SafeSortClause() string {
    allowedColumns := map[string]bool{
        "id": true, "name": true, "email": true,
        "created_at": true, "updated_at": true, "age": true,
    }
    allowedOrders := map[string]bool{
        "asc": true, "desc": true,
    }

    col := strings.ToLower(s.SortBy)
    ord := strings.ToLower(s.SortOrder)

    if !allowedColumns[col] { col = "created_at" }
    if !allowedOrders[ord]  { ord = "desc"       }

    return fmt.Sprintf("%s %s", col, ord)
}
```

### Combined Pagination + Filter + Sort Handler

```go
// GET /users?page=2&limit=10&name=rahul&role=admin&sort_by=name&sort_order=asc
func (h *UserHandler) GetUsers(c echo.Context) error {
    // ── Parse pagination ──────────────────────────────────────
    var pagination PaginationRequest
    if err := c.Bind(&pagination); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid pagination parameters",
        })
    }
    pagination.SetDefaults()

    // ── Parse filters ─────────────────────────────────────────
    var filters UserFilterRequest
    c.Bind(&filters)

    // ── Parse sorting ─────────────────────────────────────────
    var sort SortRequest
    c.Bind(&sort)
    sort.SetDefaults()

    // ── Build GORM query ──────────────────────────────────────
    query := h.db.Model(&models.User{})

    // Apply filters
    if filters.Name != "" {
        query = query.Where("name ILIKE ?", "%"+filters.Name+"%")
    }
    if filters.Email != "" {
        query = query.Where("email = ?", filters.Email)
    }
    if filters.Role != "" {
        query = query.Where("role = ?", filters.Role)
    }
    if filters.IsActive != nil {
        query = query.Where("is_active = ?", *filters.IsActive)
    }
    if filters.AgeMin > 0 {
        query = query.Where("age >= ?", filters.AgeMin)
    }
    if filters.AgeMax > 0 {
        query = query.Where("age <= ?", filters.AgeMax)
    }

    // ── Count total matching records ──────────────────────────
    var total int64
    query.Count(&total)

    // ── Apply sorting and pagination, then fetch ──────────────
    var users []models.User
    err := query.
        Order(sort.SafeSortClause()).
        Limit(pagination.Limit).
        Offset(pagination.Offset()).
        Find(&users).Error

    if err != nil {
        return c.JSON(http.StatusInternalServerError, map[string]string{
            "error": "could not fetch users",
        })
    }

    // ── Return paginated response ─────────────────────────────
    return c.JSON(http.StatusOK, NewPaginatedResponse(
        users, pagination.Page, pagination.Limit, total,
    ))
}
```

---

## Topic 5: SQL Pagination

### Pagination with Raw SQL (database/sql)

```go
// ── LIMIT and OFFSET ──────────────────────────────────────────
// LIMIT  = how many records to return
// OFFSET = how many records to skip

// Page 1: LIMIT 10 OFFSET 0
// Page 2: LIMIT 10 OFFSET 10
// Page 3: LIMIT 10 OFFSET 20

func GetUsersPaginated(db *sql.DB, page, limit int) ([]User, int64, error) {
    offset := (page - 1) * limit

    // ── Count total records ───────────────────────────────────
    var total int64
    err := db.QueryRow("SELECT COUNT(*) FROM users").Scan(&total)
    if err != nil {
        return nil, 0, fmt.Errorf("count query: %w", err)
    }

    // ── Fetch page of records ─────────────────────────────────
    rows, err := db.Query(
        `SELECT id, name, email, created_at
         FROM users
         ORDER BY created_at DESC
         LIMIT $1 OFFSET $2`,
        limit, offset,
    )
    if err != nil {
        return nil, 0, fmt.Errorf("select query: %w", err)
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var u User
        rows.Scan(&u.ID, &u.Name, &u.Email, &u.CreatedAt)
        users = append(users, u)
    }

    return users, total, rows.Err()
}
```

### Pagination with Filters in Raw SQL

```go
func GetUsersFiltered(db *sql.DB, page, limit int, name, role string) ([]User, int64, error) {
    offset := (page - 1) * limit

    // Build WHERE clause dynamically
    args    := []interface{}{}
    where   := []string{}
    argIdx  := 1

    if name != "" {
        where   = append(where, fmt.Sprintf("name ILIKE $%d", argIdx))
        args    = append(args, "%"+name+"%")
        argIdx++
    }
    if role != "" {
        where   = append(where, fmt.Sprintf("role = $%d", argIdx))
        args    = append(args, role)
        argIdx++
    }

    whereClause := ""
    if len(where) > 0 {
        whereClause = "WHERE " + strings.Join(where, " AND ")
    }

    // Count with filters
    countQuery := fmt.Sprintf("SELECT COUNT(*) FROM users %s", whereClause)
    var total int64
    db.QueryRow(countQuery, args...).Scan(&total)

    // Fetch with pagination
    args = append(args, limit, offset)
    dataQuery := fmt.Sprintf(
        `SELECT id, name, email, role, created_at
         FROM users %s
         ORDER BY created_at DESC
         LIMIT $%d OFFSET $%d`,
        whereClause, argIdx, argIdx+1,
    )

    rows, err := db.Query(dataQuery, args...)
    if err != nil {
        return nil, 0, err
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var u User
        rows.Scan(&u.ID, &u.Name, &u.Email, &u.Role, &u.CreatedAt)
        users = append(users, u)
    }

    return users, total, nil
}
```

### Cursor-Based Pagination (Alternative to Offset)

```go
// Offset pagination has a problem:
// With millions of records, OFFSET 1000000 is very slow
// Cursor-based pagination is much faster at scale

// Instead of page/limit, client sends the ID of the last seen record

// GET /users?cursor=100&limit=10
// Returns records WHERE id > 100 LIMIT 10

func GetUsersWithCursor(db *sql.DB, cursor, limit int) ([]User, int, error) {
    rows, err := db.Query(
        `SELECT id, name, email, created_at
         FROM users
         WHERE id > $1
         ORDER BY id ASC
         LIMIT $2`,
        cursor, limit,
    )
    if err != nil {
        return nil, 0, err
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var u User
        rows.Scan(&u.ID, &u.Name, &u.Email, &u.CreatedAt)
        users = append(users, u)
    }

    // Next cursor = last item's ID
    nextCursor := 0
    if len(users) > 0 {
        nextCursor = int(users[len(users)-1].ID)
    }

    return users, nextCursor, nil
}

// Response
type CursorPaginatedResponse struct {
    Data       []User `json:"data"`
    NextCursor int    `json:"next_cursor"` // 0 means no more pages
    HasMore    bool   `json:"has_more"`
}
```

### GORM Pagination Helper

```go
// Reusable paginate function for GORM
func Paginate(page, limit int) func(db *gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        if page <= 0  { page  = 1   }
        if limit <= 0 { limit = 10  }
        if limit > 100 { limit = 100 }
        offset := (page - 1) * limit
        return db.Offset(offset).Limit(limit)
    }
}

// Usage — very clean!
db.Scopes(Paginate(page, limit)).Find(&users)

// With filter and sort
db.Where("role = ?", role).
    Order("created_at DESC").
    Scopes(Paginate(page, limit)).
    Find(&users)
```

---

## Topic 6: API Query Parameters

### Complete Query Parameter Parsing

```go
// GET /api/v1/products?
//   page=2&limit=10&
//   name=laptop&min_price=500&max_price=2000&
//   category=electronics&in_stock=true&
//   sort_by=price&sort_order=asc

type ProductQueryParams struct {
    // Pagination
    Page  int `query:"page"`
    Limit int `query:"limit"`

    // Filters
    Name      string  `query:"name"`
    Category  string  `query:"category"`
    MinPrice  float64 `query:"min_price"`
    MaxPrice  float64 `query:"max_price"`
    InStock   *bool   `query:"in_stock"`

    // Sorting
    SortBy    string `query:"sort_by"`
    SortOrder string `query:"sort_order"`
}

func (h *ProductHandler) GetProducts(c echo.Context) error {
    var params ProductQueryParams

    // ── Parse all query params at once ────────────────────────
    if err := c.Bind(&params); err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "invalid query parameters",
        })
    }

    // ── Set defaults ──────────────────────────────────────────
    if params.Page  <= 0   { params.Page  = 1  }
    if params.Limit <= 0   { params.Limit = 10 }
    if params.Limit > 100  { params.Limit = 100 }
    if params.SortBy == "" { params.SortBy = "created_at" }
    if params.SortOrder == "" { params.SortOrder = "desc" }

    // ── Build query ───────────────────────────────────────────
    query := h.db.Model(&models.Product{})

    if params.Name != "" {
        query = query.Where("name ILIKE ?", "%"+params.Name+"%")
    }
    if params.Category != "" {
        query = query.Where("category = ?", params.Category)
    }
    if params.MinPrice > 0 {
        query = query.Where("price >= ?", params.MinPrice)
    }
    if params.MaxPrice > 0 {
        query = query.Where("price <= ?", params.MaxPrice)
    }
    if params.InStock != nil {
        query = query.Where("stock > 0")
    }

    // ── Count total ───────────────────────────────────────────
    var total int64
    query.Count(&total)

    // ── Apply sort + paginate + fetch ─────────────────────────
    allowedSort := map[string]bool{
        "name": true, "price": true, "created_at": true, "stock": true,
    }
    sortCol := params.SortBy
    if !allowedSort[sortCol] { sortCol = "created_at" }
    sortOrd := params.SortOrder
    if sortOrd != "asc" { sortOrd = "desc" }

    var products []models.Product
    query.
        Order(fmt.Sprintf("%s %s", sortCol, sortOrd)).
        Offset((params.Page - 1) * params.Limit).
        Limit(params.Limit).
        Find(&products)

    totalPages := int(math.Ceil(float64(total) / float64(params.Limit)))

    return c.JSON(http.StatusOK, map[string]interface{}{
        "data":        products,
        "page":        params.Page,
        "limit":       params.Limit,
        "total":       total,
        "total_pages": totalPages,
        "has_next":    params.Page < totalPages,
        "has_prev":    params.Page > 1,
        "filters": map[string]interface{}{
            "name":       params.Name,
            "category":   params.Category,
            "min_price":  params.MinPrice,
            "max_price":  params.MaxPrice,
            "in_stock":   params.InStock,
        },
        "sort": map[string]string{
            "by":    sortCol,
            "order": sortOrd,
        },
    })
}
```

### Manually Reading Query Parameters

```go
func handler(c echo.Context) error {
    // ── String params ─────────────────────────────────────────
    name    := c.QueryParam("name")     // "" if not present
    search  := c.QueryParam("search")
    category := c.QueryParam("category")

    // ── Integer params ────────────────────────────────────────
    pageStr := c.QueryParam("page")
    page, err := strconv.Atoi(pageStr)
    if err != nil || page <= 0 {
        page = 1 // default
    }

    // ── Float params ──────────────────────────────────────────
    priceStr := c.QueryParam("min_price")
    minPrice, _ := strconv.ParseFloat(priceStr, 64)

    // ── Boolean params ────────────────────────────────────────
    activeStr := c.QueryParam("is_active")
    isActive, err := strconv.ParseBool(activeStr)
    // err != nil means param wasn't provided or invalid

    // ── Array params: ?tags=go&tags=api&tags=rest ─────────────
    tags := c.QueryParams()["tags"]  // []string{"go", "api", "rest"}

    // ── With default fallback ─────────────────────────────────
    sortBy := c.QueryParam("sort_by")
    if sortBy == "" {
        sortBy = "created_at"
    }

    _ = name; _ = search; _ = category; _ = isActive; _ = tags
    return c.JSON(http.StatusOK, map[string]interface{}{
        "page":    page,
        "sort_by": sortBy,
        "min_price": minPrice,
    })
}
```

### API Response with Metadata

```go
// Best practice — always return metadata with list responses
type ListResponse struct {
    // Data
    Data interface{} `json:"data"`

    // Pagination
    Meta Meta `json:"meta"`
}

type Meta struct {
    Page       int    `json:"page"`
    Limit      int    `json:"limit"`
    Total      int64  `json:"total"`
    TotalPages int    `json:"total_pages"`
    HasNext    bool   `json:"has_next"`
    HasPrev    bool   `json:"has_prev"`

    // Applied filters (for transparency)
    Filters interface{} `json:"filters,omitempty"`
    Sort    interface{} `json:"sort,omitempty"`
}

// Example response:
// {
//   "data": [...],
//   "meta": {
//     "page": 2,
//     "limit": 10,
//     "total": 156,
//     "total_pages": 16,
//     "has_next": true,
//     "has_prev": true,
//     "filters": { "name": "rahul", "role": "admin" },
//     "sort": { "by": "created_at", "order": "desc" }
//   }
// }
```

### Testing Endpoints with curl

```bash
# Basic pagination
curl "http://localhost:8080/api/users?page=1&limit=10"

# With filters
curl "http://localhost:8080/api/users?name=rahul&role=admin"

# With sorting
curl "http://localhost:8080/api/users?sort_by=name&sort_order=asc"

# Everything combined
curl "http://localhost:8080/api/products?page=2&limit=5&name=laptop&min_price=500&sort_by=price&sort_order=desc"

# Upload image
curl -X POST http://localhost:8080/upload/image \
  -F "file=@/path/to/image.jpg"

# Upload document
curl -X POST http://localhost:8080/upload/document \
  -F "document=@/path/to/file.pdf"

# Upload multiple files
curl -X POST http://localhost:8080/upload/multiple \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.jpg"

# Download file
curl -O http://localhost:8080/download/myfile.pdf
```

---

## Interview Questions

### Topic 1–3: File Upload & Static Files

**Q: What HTTP content type is used for file uploads?**
> `multipart/form-data`. This encoding allows binary data (files) to be mixed with text fields in the same request. The request is split into parts separated by a boundary string. Each part has its own headers (Content-Disposition, Content-Type) and body.

**Q: How do you validate file type securely in Go?**
> Never trust the file extension or the Content-Type header sent by the client — both can be faked. The most secure approach is to read the first few bytes of the file and check the magic bytes (file signature). For server-side validation: use `http.DetectContentType()` which reads the actual file bytes. Also validate file extension as a secondary check.

**Q: What is a path traversal attack and how do you prevent it?**
> An attacker sends a filename like `../../etc/passwd` hoping to read sensitive files outside the upload directory. Prevent by checking `strings.Contains(filename, "..")` and `strings.Contains(filename, "/")`. Always use `filepath.Join` and validate the final path starts with your intended directory.

**Q: Why generate a new filename instead of using the original?**
> Three reasons: (1) Uniqueness — two users uploading `photo.jpg` would overwrite each other. (2) Security — original filenames may contain special characters or path separators. (3) Privacy — revealing the original filename may expose information. Use `time.Now().UnixNano()` or a UUID for unique filenames.

**Q: What is the difference between `e.Static` and `e.File` in Echo?**
> `e.Static("/prefix", "dir")` serves an entire directory — any file in that dir is accessible. `e.File("/path", "file.html")` serves one specific file. Use Static for serving a whole uploads or static folder, use File for specific files like favicon.ico or index.html.

### Topic 4–6: Pagination, Filtering, Sorting

**Q: What is the difference between offset-based and cursor-based pagination?**
> Offset-based `LIMIT 10 OFFSET 1000` skips records — gets slow on large datasets and can miss/duplicate records if data changes between requests. Cursor-based `WHERE id > last_seen_id LIMIT 10` is fast regardless of dataset size and is stable. Use offset for small datasets, cursor for large/real-time data.

**Q: How do you calculate total pages from total count?**
> `totalPages = math.Ceil(float64(total) / float64(limit))`. Always use Ceil (round up) because the last page may have fewer items than the limit. Example: 25 items, limit 10 → 25/10 = 2.5 → Ceil = 3 pages.

**Q: Why is it dangerous to directly use query param values in ORDER BY?**
> SQL injection. If you do `ORDER BY ` + sortBy, an attacker can send `sort_by=id; DROP TABLE users--`. Always whitelist allowed column names: check `sortBy` against a map of allowed columns and use only the safe value in the query. NEVER interpolate user input directly into SQL.

**Q: What does ILIKE do in PostgreSQL vs LIKE?**
> `LIKE` is case-sensitive. `ILIKE` is case-insensitive. `WHERE name LIKE '%rahul%'` matches "rahul" but not "Rahul". `WHERE name ILIKE '%rahul%'` matches both. Use ILIKE for user-facing search to give better results.

**Q: What should a paginated API response include?**
> The `data` array plus metadata: `page` (current page), `limit` (page size), `total` (total matching records), `total_pages` (calculated), `has_next` (bool), `has_prev` (bool). Optionally echo back applied filters and sort. This gives the client everything needed to render pagination controls.

**Q: How do you handle a boolean query parameter that may or may not be provided?**
> Use a pointer `*bool`. A nil pointer means the parameter wasn't provided. `false` means it was explicitly set to false. `true` means set to true. Without a pointer, you can't distinguish "not provided" from "set to false" which are very different filter behaviors.

---

## Quick Reference Cheatsheet

```go
// ── FILE UPLOAD ─────────────────────────────────────────────────
file, err := c.FormFile("file")     // single file
form, err := c.MultipartForm()       // multiple files
files := form.File["files"]          // []FileHeader

// Validate
ext  := filepath.Ext(file.Filename)  // ".jpg"
size := file.Size                    // bytes
ct   := file.Header.Get("Content-Type")

// Save
src, _ := file.Open()
dst, _ := os.Create("uploads/" + newName)
io.Copy(dst, src)
src.Close(); dst.Close()

// Form fields with file
name := c.FormValue("name")          // text field

// ── SERVE STATIC FILES ─────────────────────────────────────────
e.Static("/uploads", "uploads")      // serve directory
e.File("/favicon.ico", "static/favicon.ico") // serve one file

// Force download
c.Response().Header().Set("Content-Disposition", `attachment; filename="file.pdf"`)
return c.File(filePath)

// ── PAGINATION ─────────────────────────────────────────────────
page  := c.QueryParam("page")        // "2"
limit := c.QueryParam("limit")       // "10"
pageInt,  _ := strconv.Atoi(page)
limitInt, _ := strconv.Atoi(limit)
if pageInt  <= 0 { pageInt  = 1  }
if limitInt <= 0 { limitInt = 10 }
offset := (pageInt - 1) * limitInt

// GORM
db.Offset(offset).Limit(limitInt).Find(&items)

// Count total
var total int64
db.Model(&Item{}).Where(...).Count(&total)
totalPages := int(math.Ceil(float64(total) / float64(limitInt)))

// GORM Scope helper
func Paginate(page, limit int) func(db *gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        return db.Offset((page-1)*limit).Limit(limit)
    }
}
db.Scopes(Paginate(page, limit)).Find(&items)

// ── FILTERING ──────────────────────────────────────────────────
name := c.QueryParam("name")
if name != "" {
    query = query.Where("name ILIKE ?", "%"+name+"%")
}

// Bool filter with pointer
var isActive *bool
if s := c.QueryParam("is_active"); s != "" {
    b, _ := strconv.ParseBool(s)
    isActive = &b
}
if isActive != nil {
    query = query.Where("is_active = ?", *isActive)
}

// ── SORTING ────────────────────────────────────────────────────
allowed := map[string]bool{"name": true, "price": true, "created_at": true}
sortBy  := c.QueryParam("sort_by")
sortOrd := c.QueryParam("sort_order")
if !allowed[sortBy]     { sortBy  = "created_at" }
if sortOrd != "asc"     { sortOrd = "desc"       }
query.Order(fmt.Sprintf("%s %s", sortBy, sortOrd))

// ── CURSOR PAGINATION ──────────────────────────────────────────
cursor, _ := strconv.Atoi(c.QueryParam("cursor"))
db.Where("id > ?", cursor).Order("id ASC").Limit(limit).Find(&items)
nextCursor := items[len(items)-1].ID
```

---

## Resources

- [Echo — Static Files](https://echo.labstack.com/docs/static-files)
- [Echo — File Upload](https://echo.labstack.com/docs/cookbook/file-upload)
- [GORM — Scopes](https://gorm.io/docs/scopes.html)
- [PostgreSQL — LIMIT/OFFSET](https://www.postgresql.org/docs/current/queries-limit.html)
- [Cursor vs Offset Pagination](https://use-the-index-luke.com/no-offset)

---

*Phase 2 — File Upload · Static Files · Pagination · Filtering · Sorting — All 6 Topics Covered ✅*