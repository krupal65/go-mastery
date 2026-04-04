# 🐹 Go Language — Phase 1 Study Notes (Days 1–7)

> Complete notes for **Topic 6: Functions, Parameters, Multiple Returns** and **Topic 7: Pointers, Structs & Methods**
> Prepared for interview revision and quick reference.

---

## 📚 Table of Contents

- [Topic 6: Functions](#topic-6-functions)
  - [Function Syntax](#function-syntax)
  - [Parameters & Return Types](#parameters--return-types)
  - [Multiple Return Values](#multiple-return-values)
  - [Named Return Values](#named-return-values)
  - [Variadic Functions](#variadic-functions)
  - [Anonymous Functions](#anonymous-functions)
  - [Closures](#closures)
  - [First-Class Functions](#first-class-functions)
- [Topic 7: Pointers, Structs & Methods](#topic-7-pointers-structs--methods)
  - [Pointers](#pointers)
  - [Pointer Use Cases](#pointer-use-cases)
  - [Structs](#structs)
  - [Nested Structs](#nested-structs)
  - [Methods](#methods)
  - [Value vs Pointer Receiver](#value-vs-pointer-receiver)
- [Interview Questions](#interview-questions)

---

## Topic 6: Functions

### Function Syntax

```go
// Basic function
func greet(name string) string {
    return "Hello, " + name
}

// No return value
func printName(name string) {
    fmt.Println(name)
}

// No parameters, no return
func sayHello() {
    fmt.Println("Hello!")
}

// Multiple parameters of same type — shorthand
func add(a, b int) int {
    return a + b
}
```

---

### Parameters & Return Types

```go
// Single return
func square(n int) int {
    return n * n
}

// Return pointer
func newInt(n int) *int {
    return &n
}

// Function as parameter (higher-order function)
func apply(n int, fn func(int) int) int {
    return fn(n)
}

result := apply(5, square)   // 25
```

---

### Multiple Return Values

```go
// Multiple returns — very common Go pattern
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("cannot divide by zero")
    }
    return a / b, nil
}

// Always handle both return values
result, err := divide(10, 2)
if err != nil {
    fmt.Println("Error:", err)
    return
}
fmt.Println(result)   // 5

// Use _ to ignore a return value
result, _ := divide(10, 2)
```

---

### Named Return Values

```go
// Name the return variables in signature
func minMax(nums []int) (min int, max int) {
    min, max = nums[0], nums[0]
    for _, n := range nums {
        if n < min { min = n }
        if n > max { max = n }
    }
    return   // naked return — returns min and max automatically
}

lo, hi := minMax([]int{3, 1, 9, 4})
fmt.Println(lo, hi)   // 1 9
```

---

### Variadic Functions

```go
// ...type accepts any number of arguments
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

sum(1, 2, 3)           // 6
sum(1, 2, 3, 4, 5)     // 15

// Spread a slice with ...
nums := []int{1, 2, 3}
sum(nums...)            // 6

// Variadic must be LAST parameter
func log(prefix string, msgs ...string) {
    for _, m := range msgs {
        fmt.Println(prefix, m)
    }
}
```

---

### Anonymous Functions

```go
// Anonymous function — no name, defined inline
square := func(n int) int {
    return n * n
}
fmt.Println(square(5))   // 25

// Immediately Invoked Function Expression (IIFE)
result := func(a, b int) int {
    return a + b
}(3, 4)
fmt.Println(result)   // 7

// Anonymous function as argument
nums := []int{5, 2, 8, 1}
sort.Slice(nums, func(i, j int) bool {
    return nums[i] < nums[j]
})
```

---

### Closures

```go
// A closure captures variables from its surrounding scope
func counter() func() int {
    count := 0             // captured variable
    return func() int {
        count++
        return count
    }
}

c1 := counter()
fmt.Println(c1())   // 1
fmt.Println(c1())   // 2
fmt.Println(c1())   // 3

c2 := counter()     // new independent counter
fmt.Println(c2())   // 1  (fresh start)
fmt.Println(c1())   // 4  (c1 continues)
```

> 💡 Each call to `counter()` creates a new independent closure with its own `count` variable.

---

### First-Class Functions

```go
// Functions are values — can be stored in variables
var fn func(int) int = square

// Functions in maps
ops := map[string]func(int, int) int{
    "add": func(a, b int) int { return a + b },
    "sub": func(a, b int) int { return a - b },
    "mul": func(a, b int) int { return a * b },
}
fmt.Println(ops["add"](3, 4))   // 7
fmt.Println(ops["mul"](3, 4))   // 12

// Return a function from a function
func multiplier(factor int) func(int) int {
    return func(n int) int {
        return n * factor
    }
}
double := multiplier(2)
triple := multiplier(3)
fmt.Println(double(5))   // 10
fmt.Println(triple(5))   // 15
```

---

## Topic 7: Pointers, Structs & Methods

### Pointers

```go
// & = address of variable (get pointer)
// * = dereference pointer (get value at address)

x := 42
p := &x              // p is a pointer to x, type: *int

fmt.Println(x)       // 42   (value)
fmt.Println(p)       // 0xc0000b4010  (memory address)
fmt.Println(*p)      // 42   (dereferenced value)

// Modify original through pointer
*p = 100
fmt.Println(x)       // 100  (x changed!)

// new() — allocates memory and returns pointer
ptr := new(int)      // *int pointing to 0
*ptr = 55
fmt.Println(*ptr)    // 55
```

---

### Pointer Use Cases

```go
// Use case 1: Modify a variable inside a function
func increment(n *int) {
    *n++
}
x := 10
increment(&x)
fmt.Println(x)   // 11  ✅ (modified)

// Without pointer — original NOT modified
func incrementNoPtr(n int) {
    n++   // only local copy changes
}
incrementNoPtr(x)
fmt.Println(x)   // 11  (unchanged)

// Use case 2: Avoid copying large structs
type BigStruct struct { data [1000]int }

func process(s *BigStruct) {   // pass pointer, not copy
    s.data[0] = 99
}

// Use case 3: nil pointer check
var p *int
if p == nil {
    fmt.Println("pointer is nil")   // always check before dereferencing!
}
// *p = 5  // ❌ panic: nil pointer dereference
```

---

### Structs

```go
// Define a struct
type Person struct {
    Name string
    Age  int
    City string
}

// Create struct — 3 ways
p1 := Person{Name: "Rahul", Age: 25, City: "Surat"}   // named fields ✅ preferred
p2 := Person{"Priya", 23, "Mumbai"}                    // positional (order matters)
var p3 Person                                           // zero value struct

// Access fields
fmt.Println(p1.Name)   // Rahul
fmt.Println(p1.Age)    // 25

// Modify fields
p1.Age = 26

// Pointer to struct — use . not ->
pp := &p1
pp.Name = "Rahul Kumar"   // Go auto-dereferences: same as (*pp).Name
fmt.Println(p1.Name)       // Rahul Kumar
```

---

### Nested Structs

```go
type Address struct {
    Street string
    City   string
    State  string
}

type Employee struct {
    Name    string
    Age     int
    Address Address   // nested struct
}

e := Employee{
    Name: "Arjun",
    Age:  28,
    Address: Address{
        Street: "MG Road",
        City:   "Surat",
        State:  "Gujarat",
    },
}

fmt.Println(e.Address.City)    // Surat
fmt.Println(e.Address.State)   // Gujarat

// Anonymous/embedded struct
type Manager struct {
    Employee          // embedded — promotes fields
    Department string
}

m := Manager{Employee: e, Department: "Engineering"}
fmt.Println(m.Name)         // Arjun (promoted from Employee)
fmt.Println(m.Department)   // Engineering
```

---

### Methods

```go
// Method = function with a receiver
// Receiver goes between func keyword and method name

type Rectangle struct {
    Width  float64
    Height float64
}

// Value receiver — works on a copy
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

func (r Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}

func (r Rectangle) String() string {
    return fmt.Sprintf("Rectangle(%.1f x %.1f)", r.Width, r.Height)
}

rect := Rectangle{Width: 10, Height: 5}
fmt.Println(rect.Area())       // 50
fmt.Println(rect.Perimeter())  // 30
fmt.Println(rect.String())     // Rectangle(10.0 x 5.0)
```

---

### Value vs Pointer Receiver

```go
type Counter struct {
    count int
}

// Value receiver — gets a COPY, original NOT modified
func (c Counter) GetCount() int {
    return c.count
}

// Pointer receiver — modifies the ORIGINAL
func (c *Counter) Increment() {
    c.count++
}

func (c *Counter) Reset() {
    c.count = 0
}

c := Counter{}
c.Increment()   // count = 1
c.Increment()   // count = 2
c.Increment()   // count = 3
fmt.Println(c.GetCount())   // 3
c.Reset()
fmt.Println(c.GetCount())   // 0
```

**When to use which receiver:**

| Situation | Use |
|---|---|
| Need to modify the struct | Pointer receiver `*T` |
| Struct is large (avoid copy) | Pointer receiver `*T` |
| Read-only, small struct | Value receiver `T` |
| Consistency — if any method uses pointer, use for all | Pointer receiver `*T` |

```go
// Go automatically takes address when needed
c := Counter{}
c.Increment()    // Go converts this to (&c).Increment() automatically
```

---

## Interview Questions

### Topic 6: Functions

**Q: What is a variadic function? How do you call it with a slice?**
> A variadic function accepts any number of arguments using `...type`. To pass a slice, use the spread operator: `sum(nums...)`. The variadic parameter must always be the last parameter.

**Q: What is a closure in Go?**
> A closure is a function that captures and remembers variables from its surrounding scope even after the outer function has returned. Each closure gets its own copy of the captured variable. Commonly used for counters, generators, and middleware.

**Q: What is the difference between a function and a method in Go?**
> A function is standalone: `func add(a, b int) int`. A method is attached to a type via a receiver: `func (r Rectangle) Area() float64`. Methods allow you to define behavior on your custom types.

**Q: What are first-class functions in Go?**
> In Go, functions are values — they can be stored in variables, passed as arguments, and returned from other functions. This enables functional patterns like `map`, `filter`, `reduce`, and middleware chains.

**Q: What is the difference between named and unnamed return values?**
> Named return values declare variables in the signature: `func f() (x int, y int)`. A naked `return` at the end returns those variables. Useful for short, clear functions. Unnamed returns require explicit `return x, y`.

**Q: What is an IIFE in Go?**
> An Immediately Invoked Function Expression — an anonymous function defined and called in the same statement: `result := func(a, b int) int { return a + b }(3, 4)`. Used for one-off logic or goroutine blocks.

---

### Topic 7: Pointers, Structs & Methods

**Q: What is the difference between & and * in Go?**
> `&` gives the memory address of a variable (creates a pointer). `*` dereferences a pointer (gets the value at the address). Example: `p := &x` stores address, `*p` reads/writes the value at that address.

**Q: What happens if you dereference a nil pointer?**
> The program panics at runtime with "nil pointer dereference". Always check `if p == nil` before dereferencing. This is one of the most common runtime errors in Go.

**Q: What is the difference between value receiver and pointer receiver?**
> Value receiver `(t T)` gets a copy — changes don't affect the original. Pointer receiver `(t *T)` gets the address — changes modify the original. Use pointer receiver when you need to mutate the struct or when the struct is large.

**Q: How do you create a struct in Go?**
> Three ways: (1) Named fields: `Person{Name: "Rahul", Age: 25}` — preferred, order-independent. (2) Positional: `Person{"Rahul", 25}` — order must match declaration. (3) Zero value: `var p Person` — all fields get zero values.

**Q: What is struct embedding in Go?**
> Embedding one struct inside another promotes the embedded struct's fields and methods to the outer struct. `type Manager struct { Employee }` means you can call `m.Name` directly instead of `m.Employee.Name`. This is Go's way of achieving composition.

**Q: Does Go have -> operator like C for pointer to struct?**
> No. Go uses `.` for both regular and pointer access to struct fields. When you do `pp.Name` on a pointer, Go automatically dereferences it — same as `(*pp).Name`. No `->` needed.

**Q: When should you use a pointer receiver vs value receiver?**
> Use pointer receiver when: (1) the method needs to modify the struct, (2) the struct is large and you want to avoid copying, (3) consistency — if any method needs a pointer receiver, make all methods pointer receivers.

---

## Quick Reference Cheatsheet

```go
// ── FUNCTIONS ──────────────────────────────────────────
func add(a, b int) int { return a + b }           // basic
func div(a, b float64) (float64, error) { ... }   // multi-return
func sum(nums ...int) int { ... }                  // variadic
sum(nums...)                                       // spread slice

// named return
func minMax(n []int) (min, max int) { ...; return }

// anonymous + closure
sq := func(n int) int { return n * n }
func counter() func() int {
    c := 0
    return func() int { c++; return c }
}

// first-class
ops := map[string]func(int,int)int{ "add": func(a,b int)int{return a+b} }

// ── POINTERS ───────────────────────────────────────────
x := 42
p := &x        // pointer to x
*p = 100       // modify through pointer
ptr := new(int) // allocate + pointer

func inc(n *int) { *n++ }   // modify via pointer
inc(&x)

// ── STRUCTS ────────────────────────────────────────────
type Person struct { Name string; Age int }

p := Person{Name: "Rahul", Age: 25}  // named ✅
p.Name = "Kumar"                      // access/modify
pp := &p; pp.Name = "New"             // pointer — auto deref

// ── METHODS ────────────────────────────────────────────
func (r Rectangle) Area() float64 { ... }    // value receiver
func (c *Counter) Increment() { c.count++ }  // pointer receiver
```

---

## Resources

- [Official Go Documentation](https://go.dev/doc/)
- [Go Tour — Methods](https://go.dev/tour/methods)
- [Go Playground](https://go.dev/play/)
- [Effective Go](https://go.dev/doc/effective_go)

---

*Phase 1 — Days 1-7 | Topics 6 & 7 covered*