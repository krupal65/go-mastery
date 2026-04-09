# 🐹 Go Language — Phase 1 Study Notes (Days 1–7)

> Complete notes for the **Last 3 Topics of Phase 1:**
> - **Topic 11: Working with Packages & Modules**
> - **Topic 12: Go Concurrency Basics & Goroutines**
> - **Topic 13: Channels and Select Statement**

---

## 📚 Table of Contents

- [Topic 11: Working with Packages & Modules](#topic-11-working-with-packages--modules)
  - [What is a Package?](#what-is-a-package)
  - [Exported vs Unexported Names](#exported-vs-unexported-names)
  - [Importing Packages](#importing-packages)
  - [Go Modules — go.mod](#go-modules--gomod)
  - [Module Commands](#module-commands)
  - [init() Function](#init-function)
  - [Standard Library Packages](#standard-library-packages)
- [Topic 12: Go Concurrency Basics & Goroutines](#topic-12-go-concurrency-basics--goroutines)
  - [What is Concurrency?](#what-is-concurrency)
  - [Goroutines](#goroutines)
  - [Goroutine vs OS Thread](#goroutine-vs-os-thread)
  - [sync.WaitGroup](#syncwaitgroup)
  - [sync.Mutex](#syncmutex)
  - [Race Condition](#race-condition)
  - [sync.Once](#synconce)
  - [Worker Pool Pattern](#worker-pool-pattern)
- [Topic 13: Channels and Select Statement](#topic-13-channels-and-select-statement)
  - [What is a Channel?](#what-is-a-channel)
  - [Unbuffered vs Buffered Channel](#unbuffered-vs-buffered-channel)
  - [Channel Directions](#channel-directions)
  - [Range over Channel](#range-over-channel)
  - [Select Statement](#select-statement)
  - [Select with Default](#select-with-default)
  - [Select with Timeout](#select-with-timeout)
  - [done Channel Pattern](#done-channel-pattern)
  - [Pipeline Pattern](#pipeline-pattern)
- [Interview Questions](#interview-questions)
- [Quick Reference Cheatsheet](#quick-reference-cheatsheet)

---

## Topic 11: Working with Packages & Modules

### What is a Package?

A **package** is a directory of `.go` files that all share the same `package` declaration at the top. Every Go file must belong to a package.

```go
package main    // executable program — entry point is func main()
package utils   // library package — reusable code
package models  // another library package
```

> 📌 The package name is usually the last segment of the import path. If you import `"github.com/user/project/utils"`, you use it as `utils.FunctionName()`.

---

### Exported vs Unexported Names

Go has only ONE rule for access control — **the first letter of the name**:

```go
// ✅ EXPORTED (public) — starts with UPPERCASE
// Accessible from any package that imports this one
func Add(a, b int) int        { return a + b }
type User struct               { Name string; Age int }
var  MaxRetries = 3
const Version   = "1.0.0"

// ❌ UNEXPORTED (private) — starts with lowercase
// Accessible only within the same package
func helper() {}
type internalState struct {}
var  counter int
```

> 💡 No `public`, `private`, `protected` keywords in Go — only uppercase vs lowercase. This applies to functions, types, variables, constants, and even struct fields.

---

### Importing Packages

```go
// Single import
import "fmt"

// Multiple imports — preferred grouped style
import (
    "fmt"
    "math"
    "strings"
    "strconv"
)

// Import with alias
import (
    f   "fmt"              // use as f.Println()
    str "strings"          // use as str.ToUpper()
)

// Blank import — import only for side effects (init())
import _ "github.com/lib/pq"   // registers postgres driver

// Import your own package
import "github.com/yourname/myproject/utils"

func main() {
    result := utils.Add(5, 3)   // only exported names work
    fmt.Println(result)
}
```

> ⚠️ **Unused imports = compile error.** Go enforces this strictly. Use `_` for side-effect-only imports.

---

### Go Modules — go.mod

A **module** is a collection of packages defined by a `go.mod` file at the root of the project. The module path is the unique identifier for your project.

```bash
# Create a new module
go mod init github.com/yourname/myproject
```

```go
// go.mod — automatically created and managed
module github.com/yourname/myproject

go 1.21

require (
    github.com/gin-gonic/gin  v1.9.1
    github.com/stretchr/testify v1.8.4
)
```

**Project structure with modules:**

```
myproject/
├── go.mod              ← module definition
├── go.sum              ← checksums (never edit manually)
├── main.go             ← package main
├── utils/
│   ├── math.go         ← package utils
│   └── string.go       ← package utils
├── models/
│   └── user.go         ← package models
└── handlers/
    └── user.go         ← package handlers
```

---

### Module Commands

```bash
# Initialize a new module
go mod init github.com/user/myproject

# Add a dependency
go get github.com/gin-gonic/gin@latest
go get github.com/gin-gonic/gin@v1.9.1     # specific version

# Remove unused, add missing dependencies
go mod tidy

# Download all dependencies
go mod download

# Show dependency graph
go mod graph

# Verify checksums
go mod verify
```

| Command | What it does |
|---|---|
| `go mod init` | Creates go.mod with module path |
| `go get pkg@version` | Adds/updates a dependency |
| `go mod tidy` | Cleans up go.mod and go.sum |
| `go mod download` | Downloads all dependencies |
| `go build` | Compiles the package |
| `go run main.go` | Compiles and runs |
| `go test ./...` | Runs all tests |

---

### init() Function

```go
// init() runs automatically BEFORE main() when package is imported
// You cannot call it manually
// Each file can have multiple init() functions
// They run in the order they are defined

package db

import (
    "database/sql"
    "log"
)

var DB *sql.DB

func init() {
    var err error
    DB, err = sql.Open("postgres", "connection_string_here")
    if err != nil {
        log.Fatal("Database connection failed:", err)
    }
    log.Println("Database connected")
}

// Order of execution:
// 1. Package-level variables initialized
// 2. init() functions run
// 3. main() runs
```

---

### Standard Library Packages

| Package | Primary Use |
|---|---|
| `fmt` | Formatted I/O — print, scan, sprintf |
| `errors` | Error creation and inspection |
| `strings` | String manipulation — split, join, trim, replace |
| `strconv` | Type conversions — Itoa, Atoi, ParseFloat |
| `math` | Math functions — Sqrt, Abs, Floor, Ceil |
| `os` | OS operations — files, env vars, exit |
| `io` | Reader/Writer interfaces |
| `bufio` | Buffered I/O |
| `sync` | Mutex, WaitGroup, Once, RWMutex |
| `sync/atomic` | Atomic operations for concurrent use |
| `time` | Time, Duration, Timer, Ticker |
| `context` | Request context, cancellation, deadlines |
| `log` | Simple logging |
| `sort` | Sorting slices and custom types |
| `encoding/json` | JSON marshal and unmarshal |
| `net/http` | HTTP server and client |
| `testing` | Unit testing and benchmarks |
| `path/filepath` | File path manipulation |

---

## Topic 12: Go Concurrency Basics & Goroutines

### What is Concurrency?

**Concurrency** means multiple tasks are in progress at the same time (not necessarily running simultaneously). Go has built-in concurrency through goroutines and channels — no need for external libraries.

> Go proverb: **"Concurrency is not parallelism."**
> Concurrency = dealing with many things at once (design).
> Parallelism = doing many things at once (execution).

---

### Goroutines

A goroutine is a **lightweight thread** managed by the Go runtime — not an OS thread.

```go
// Launch a goroutine with the go keyword
go functionName()

// Anonymous goroutine
go func() {
    fmt.Println("running concurrently")
}()

// Pass arguments
go func(name string) {
    fmt.Println("Hello,", name)
}("Rahul")

// Example
func sayHello(name string) {
    fmt.Printf("Hello, %s!\n", name)
}

func main() {
    go sayHello("Rahul")   // runs concurrently
    go sayHello("Priya")   // runs concurrently
    go sayHello("Arjun")   // runs concurrently

    time.Sleep(100 * time.Millisecond)   // wait for goroutines
    fmt.Println("Done")
}
// Output order is NOT guaranteed — goroutines are concurrent!
```

---

### Goroutine vs OS Thread

| Feature | Goroutine | OS Thread |
|---|---|---|
| Initial stack size | ~2–8 KB | ~1–8 MB |
| Stack growth | Dynamic (grows/shrinks) | Fixed |
| Creation cost | Very cheap | Expensive |
| Context switching | Go runtime (fast) | OS kernel (slow) |
| How many can you run? | Millions | Thousands max |
| Managed by | Go runtime scheduler | Operating system |

---

### sync.WaitGroup

`WaitGroup` lets you wait for a collection of goroutines to finish.

```go
import "sync"

func main() {
    var wg sync.WaitGroup

    for i := 1; i <= 5; i++ {
        wg.Add(1)                    // 1. increment BEFORE launching goroutine
        go func(n int) {             // 2. pass loop var as argument (important!)
            defer wg.Done()          // 3. decrement when goroutine finishes
            fmt.Printf("Worker %d done\n", n)
        }(i)                         // pass i by value here
    }

    wg.Wait()   // blocks main until counter reaches 0
    fmt.Println("All workers finished!")
}
```

> ⚠️ **Loop variable trap:** Never capture the loop variable `i` directly inside a goroutine. By the time the goroutine runs, `i` may already be at its final value. Always pass it as a function argument `func(n int){...}(i)` to give each goroutine its own copy.

```go
// ❌ WRONG — all goroutines may print the same value
for i := 0; i < 3; i++ {
    go func() {
        fmt.Println(i)   // i is shared — race condition!
    }()
}

// ✅ CORRECT — each goroutine gets its own copy
for i := 0; i < 3; i++ {
    go func(n int) {
        fmt.Println(n)   // n is a copy, safe!
    }(i)
}
```

---

### sync.Mutex

A `Mutex` (Mutual Exclusion lock) protects shared data from concurrent access.

```go
import "sync"

type SafeCounter struct {
    mu    sync.Mutex
    count int
}

// Pointer receiver — modifies the struct
func (c *SafeCounter) Increment() {
    c.mu.Lock()           // acquire lock — blocks if another goroutine holds it
    defer c.mu.Unlock()   // always use defer — releases even on panic
    c.count++
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}

func main() {
    counter := SafeCounter{}
    var wg sync.WaitGroup

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter.Increment()
        }()
    }

    wg.Wait()
    fmt.Println(counter.Value())   // always 1000 — race-free ✅
}
```

**sync.RWMutex — better for read-heavy workloads:**

```go
var rw sync.RWMutex

// Multiple readers can hold the lock simultaneously
rw.RLock()
defer rw.RUnlock()
// read data...

// Only one writer at a time, blocks all readers
rw.Lock()
defer rw.Unlock()
// write data...
```

---

### Race Condition

```go
// ❌ Race condition — concurrent writes without synchronization
count := 0
var wg sync.WaitGroup

for i := 0; i < 1000; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        count++   // DATA RACE! Multiple goroutines writing count
    }()
}
wg.Wait()
fmt.Println(count)   // unpredictable — could be anything!

// Detect race conditions with the race detector:
// go run -race main.go
// go test -race ./...
```

---

### sync.Once

Ensures a function is called exactly once — useful for lazy initialization.

```go
var (
    instance *Database
    once     sync.Once
)

func GetDatabase() *Database {
    once.Do(func() {
        instance = &Database{} // runs only the FIRST time
        instance.Connect()
    })
    return instance   // subsequent calls return same instance
}

// Safe to call from multiple goroutines
db1 := GetDatabase()
db2 := GetDatabase()
// db1 == db2 — same instance, connected only once
```

---

### Worker Pool Pattern

Distribute work across a fixed number of goroutines to limit resource usage:

```go
func workerPool(jobs []int, numWorkers int) []int {
    jobCh    := make(chan int, len(jobs))
    resultCh := make(chan int, len(jobs))

    // Start N workers
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobCh {
                resultCh <- job * job   // process job
            }
        }()
    }

    // Send all jobs
    for _, j := range jobs { jobCh <- j }
    close(jobCh)   // signal workers: no more jobs

    // Wait for workers then close results
    go func() {
        wg.Wait()
        close(resultCh)
    }()

    // Collect results
    results := []int{}
    for r := range resultCh {
        results = append(results, r)
    }
    return results
}
```

---

## Topic 13: Channels and Select Statement

### What is a Channel?

A channel is a **typed pipe** through which goroutines send and receive values. Channels both communicate data AND synchronize goroutines.

> Go proverb: **"Do not communicate by sharing memory; instead, share memory by communicating."**

```go
// Create a channel
ch := make(chan int)        // unbuffered channel
ch := make(chan string, 5)  // buffered channel with capacity 5

// Send a value (blocks for unbuffered until receiver is ready)
ch <- 42
ch <- "hello"

// Receive a value (blocks until sender sends)
val := <-ch

// Receive with closed check
val, ok := <-ch    // ok = false when channel is closed and empty

// Close a channel (SENDER only!)
close(ch)
```

---

### Unbuffered vs Buffered Channel

```go
// ── UNBUFFERED ──────────────────────────────────────────────
// Send BLOCKS until a receiver is ready
// Guarantees synchronization between sender and receiver

ch := make(chan int)

go func() {
    ch <- 42   // blocks here until main receives
}()

val := <-ch   // receives 42, goroutine unblocks
fmt.Println(val)

// ── BUFFERED ────────────────────────────────────────────────
// Send only BLOCKS when buffer is full
// Receiver only BLOCKS when buffer is empty

ch := make(chan int, 3)
ch <- 1   // doesn't block — buffer has space
ch <- 2   // doesn't block
ch <- 3   // doesn't block
// ch <- 4  // BLOCKS — buffer full!

fmt.Println(<-ch)   // 1  (FIFO order)
fmt.Println(<-ch)   // 2
fmt.Println(<-ch)   // 3
```

| | Unbuffered | Buffered |
|---|---|---|
| Created with | `make(chan T)` | `make(chan T, n)` |
| Send blocks when | No receiver ready | Buffer full |
| Receive blocks when | No sender ready | Buffer empty |
| Synchronization | Guaranteed | Not guaranteed |
| Use case | Tight sync needed | Decouple sender/receiver |

---

### Channel Directions

Restrict what a function can do with a channel for safety:

```go
// Send-only channel — can only SEND, not receive
func producer(ch chan<- int) {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    close(ch)   // producer closes the channel
}

// Receive-only channel — can only RECEIVE, not send
func consumer(ch <-chan int) {
    for val := range ch {
        fmt.Println("Received:", val)
    }
}

func main() {
    ch := make(chan int, 5)
    go producer(ch)     // ch is automatically narrowed to chan<-int
    consumer(ch)        // ch is automatically narrowed to <-chan int
}
```

> 💡 Directional channels prevent bugs — if a function accidentally tries to send on a receive-only channel, it's a compile error, not a runtime panic.

---

### Range over Channel

```go
ch := make(chan int, 5)

// Producer — sends values and closes
go func() {
    for i := 1; i <= 5; i++ {
        ch <- i
    }
    close(ch)   // MUST close — otherwise range blocks forever!
}()

// Consumer — receives until channel is closed
for val := range ch {
    fmt.Println(val)   // 1 2 3 4 5
}
fmt.Println("Channel closed, loop ended")
```

> ⚠️ Always close the channel from the **sender side** after sending all values. `range` over an unclosed channel will block forever — causing a deadlock.

---

### Select Statement

`select` lets a goroutine wait on **multiple channel operations** at once — like a `switch` but for channels.

```go
ch1 := make(chan string)
ch2 := make(chan string)

go func() { time.Sleep(1 * time.Second); ch1 <- "one" }()
go func() { time.Sleep(2 * time.Second); ch2 <- "two" }()

// select blocks until one case is ready
for i := 0; i < 2; i++ {
    select {
    case msg := <-ch1:
        fmt.Println("Received from ch1:", msg)
    case msg := <-ch2:
        fmt.Println("Received from ch2:", msg)
    }
}
// Output:
// Received from ch1: one   (after 1 second)
// Received from ch2: two   (after 2 seconds)
```

> 📌 If **multiple cases are ready** at the same time, Go picks one **at random** — this prevents starvation.

---

### Select with Default

Adding a `default` case makes `select` non-blocking:

```go
ch := make(chan int, 1)

// Non-blocking receive
select {
case val := <-ch:
    fmt.Println("Received:", val)
default:
    fmt.Println("No value ready — moving on")
}

// Non-blocking send
select {
case ch <- 42:
    fmt.Println("Sent 42")
default:
    fmt.Println("Channel full — could not send")
}
```

---

### Select with Timeout

```go
import "time"

func fetchWithTimeout(id int) (string, error) {
    resultCh := make(chan string, 1)

    go func() {
        time.Sleep(3 * time.Second)   // simulate slow work
        resultCh <- fmt.Sprintf("data for id=%d", id)
    }()

    select {
    case result := <-resultCh:
        return result, nil
    case <-time.After(2 * time.Second):   // timeout after 2 seconds
        return "", fmt.Errorf("request timed out after 2s")
    }
}

result, err := fetchWithTimeout(1)
if err != nil {
    fmt.Println("Error:", err)   // Error: request timed out after 2s
} else {
    fmt.Println(result)
}
```

---

### done Channel Pattern

Signal goroutines to stop gracefully using a `done` channel:

```go
func worker(id int, done <-chan struct{}) {
    for {
        select {
        case <-done:
            fmt.Printf("Worker %d stopping\n", id)
            return
        default:
            fmt.Printf("Worker %d doing work\n", id)
            time.Sleep(100 * time.Millisecond)
        }
    }
}

func main() {
    done := make(chan struct{})   // struct{} — zero size, no data needed

    for i := 1; i <= 3; i++ {
        go worker(i, done)
    }

    time.Sleep(500 * time.Millisecond)
    close(done)   // closing broadcasts to ALL goroutines reading from done

    time.Sleep(100 * time.Millisecond)
    fmt.Println("All workers stopped")
}
```

> 💡 Use `chan struct{}` for signal-only channels — `struct{}` takes zero bytes of memory.
> Closing a channel **broadcasts** to all goroutines reading from it — they all unblock.

---

### Pipeline Pattern

Connect goroutines using channels to form a processing pipeline:

```go
// Stage 1: Generate numbers
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

// Stage 2: Square each number
func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// Stage 3: Filter even numbers
func filterEven(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            if n%2 == 0 {
                out <- n
            }
        }
        close(out)
    }()
    return out
}

func main() {
    // Connect stages: generate → square → filterEven → print
    nums    := generate(1, 2, 3, 4, 5)
    squares := square(nums)
    evens   := filterEven(squares)

    for n := range evens {
        fmt.Println(n)   // 4, 16 (squares of 2 and 4)
    }
}
```

---

## Interview Questions

### Topic 11: Packages & Modules

**Q: What is the difference between a package and a module in Go?**
> A package is a directory of `.go` files with the same `package` declaration. A module is a collection of packages defined by a `go.mod` file at the root. A module has a unique path like `github.com/user/project` and manages all dependencies.

**Q: What makes a name exported in Go?**
> A name is exported if it starts with an uppercase letter. Exported names are accessible from other packages. Lowercase names are package-private. This applies to functions, types, variables, constants, and struct fields. No `public`/`private` keywords.

**Q: What happens if you import a package and don't use it?**
> Compile error. Go enforces no unused imports. Use `import _ "pkg"` if you only need the side effects (like running the package's `init()` function to register a database driver).

**Q: What does `go mod tidy` do?**
> It adds any missing module requirements and removes unused ones from `go.mod` and `go.sum`. Run it after adding or removing imports to keep the module files clean and accurate.

**Q: What is the purpose of the `init()` function?**
> `init()` runs automatically before `main()` when the package is imported. Used for one-time setup like database connections, config loading, registering drivers. You cannot call it manually. Each file can have multiple `init()` functions.

---

### Topic 12: Goroutines

**Q: What is a goroutine and how is it different from an OS thread?**
> A goroutine is a lightweight concurrent function managed by the Go runtime. Unlike OS threads (~1MB stack), goroutines start with only ~2-8KB and grow dynamically. You can run millions of goroutines. Context switching is done by the Go scheduler, not the OS kernel — much faster and cheaper.

**Q: What is `sync.WaitGroup` used for?**
> To wait for a collection of goroutines to finish. Call `wg.Add(1)` before each goroutine, `wg.Done()` inside (usually with `defer`), and `wg.Wait()` in the main goroutine to block until all goroutines complete.

**Q: What is a race condition and how do you detect it in Go?**
> A race condition occurs when multiple goroutines access shared data concurrently and at least one goroutine writes, without proper synchronization. Detect with `go run -race main.go`. Fix with `sync.Mutex`, channels, or `sync/atomic`.

**Q: Why should you pass loop variables as arguments to goroutines?**
> If a goroutine captures a loop variable directly, all goroutines share the same variable and see its final value when they execute. Passing it as an argument `go func(n int){...}(i)` gives each goroutine its own copy of the value at the time of launch.

**Q: What is `sync.Once` used for?**
> Ensures a function executes exactly once, even when called from multiple goroutines simultaneously. Used for lazy initialization of singletons like database connections or configuration loading.

**Q: What is the difference between `sync.Mutex` and `sync.RWMutex`?**
> `Mutex` allows only one goroutine to hold the lock at a time (for both reads and writes). `RWMutex` allows multiple goroutines to hold the read lock simultaneously (`RLock`), but only one for writing (`Lock`). Use `RWMutex` for read-heavy workloads.

---

### Topic 13: Channels & Select

**Q: What is a channel in Go?**
> A typed pipe for communication between goroutines. Goroutines send values with `ch <- val` and receive with `val := <-ch`. Channels both transfer data and synchronize goroutines without explicit locks.

**Q: What is the difference between buffered and unbuffered channels?**
> Unbuffered `make(chan T)` — send blocks until a receiver is ready. Forces synchronization. Buffered `make(chan T, n)` — send only blocks when the buffer is full. The sender can proceed without an immediate receiver. Use buffered to decouple sender and receiver speed.

**Q: Who should close a channel — sender or receiver?**
> Only the **sender** should close a channel. Sending to a closed channel panics at runtime. Receiving from a closed channel returns the zero value and `ok=false`. Closing signals receivers that no more values will be sent.

**Q: What does the `select` statement do?**
> `select` waits on multiple channel operations and executes the first case that is ready. If multiple cases are ready simultaneously, one is chosen at random (prevents starvation). Adding a `default` case makes it non-blocking.

**Q: How do you implement a timeout using channels?**
> Use `time.After(duration)` which returns a `<-chan Time` that receives after the duration: `select { case res := <-ch: ... case <-time.After(2*time.Second): // handle timeout }`.

**Q: What is the `done` channel pattern?**
> A `chan struct{}` used to signal goroutines to stop. When `close(done)` is called, all goroutines reading from it unblock simultaneously — a broadcast. Use `struct{}` because it takes zero bytes of memory.

**Q: What is the concurrency proverb of Go?**
> "Do not communicate by sharing memory; instead, share memory by communicating." Use channels to pass data between goroutines rather than sharing variables protected by mutexes. Channels make data ownership explicit.

**Q: What happens when you range over an unclosed channel?**
> The program deadlocks. `range ch` blocks waiting for the next value. If the channel is never closed, it blocks forever. Always close the channel from the sender side after all values are sent when using `range`.

---

## Quick Reference Cheatsheet

```go
// ── PACKAGES & MODULES ─────────────────────────────────────────
package main                          // executable
package utils                         // library

func ExportedFunc() {}                // UPPERCASE = public
func privateFunc() {}                 // lowercase = package-private

import (
    "fmt"
    alias "strings"                   // alias import
    _     "github.com/lib/pq"         // side effects only
)

// go mod init github.com/user/myapp
// go get pkg@version
// go mod tidy

// ── GOROUTINES ─────────────────────────────────────────────────
go myFunc()                           // launch goroutine
go func(n int) { ... }(i)            // pass loop var by value!

var wg sync.WaitGroup
wg.Add(1)
go func() { defer wg.Done(); ... }()
wg.Wait()                             // wait for all

var mu sync.Mutex
mu.Lock(); defer mu.Unlock()          // protect shared data

var once sync.Once
once.Do(func() { /* runs once */ })   // singleton init

// go run -race main.go               // detect race conditions

// ── CHANNELS ───────────────────────────────────────────────────
ch := make(chan int)                   // unbuffered
ch := make(chan int, 10)              // buffered
ch <- val                             // send (blocks if no receiver/full)
val := <-ch                           // receive (blocks if empty)
val, ok := <-ch                       // ok=false if closed+empty
close(ch)                             // sender closes only!
for v := range ch { }                 // range (MUST close ch!)

func send(ch chan<- int) {}            // send-only
func recv(ch <-chan int) {}            // receive-only

// done pattern
done := make(chan struct{})
close(done)                           // broadcasts to all readers

// ── SELECT ─────────────────────────────────────────────────────
select {
case v := <-ch1:                      // receive from ch1
case ch2 <- val:                      // send to ch2
case <-time.After(2 * time.Second):  // timeout
default:                              // non-blocking fallback
}

// ── PATTERNS ───────────────────────────────────────────────────
// Pipeline:  generate → stage1 → stage2 → consume
// Worker pool: N goroutines reading from jobs channel
// Fan-out: 1 producer → N consumers
// Fan-in: N producers → 1 consumer (merge)
// Timeout: select + time.After
// Cancellation: done channel + close(done)
```

---

## Resources

- [Go Tour — Packages](https://go.dev/tour/basics/1)
- [Go Tour — Concurrency](https://go.dev/tour/concurrency)
- [Go by Example — Goroutines](https://gobyexample.com/goroutines)
- [Go by Example — Channels](https://gobyexample.com/channels)
- [Go by Example — Select](https://gobyexample.com/select)
- [Effective Go — Concurrency](https://go.dev/doc/effective_go#concurrency)

---

*Phase 1 — Days 1-7 | Topics 11, 12 & 13 — COMPLETE ✅*
*Phase 1 Fully Complete — All 13 Topics Done! 🎉*