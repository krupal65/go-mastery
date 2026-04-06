# 🐹 Go Language — Phase 1 Study Notes (Days 1–7)

> Complete notes for **Topic 8: Interfaces & Error Handling** and **Topic 9: Interfaces in Go (Deep Dive)**
> Prepared for interview revision and quick reference.

---

## 📚 Table of Contents

- [Topic 8: Interfaces & Error Handling](#topic-8-interfaces--error-handling)
  - [What is an Interface?](#what-is-an-interface)
  - [Implementing an Interface](#implementing-an-interface)
  - [Interface with Multiple Types](#interface-with-multiple-types)
  - [Empty Interface](#empty-interface)
  - [Error Handling](#error-handling)
  - [Custom Errors](#custom-errors)
  - [Error Wrapping (Go 1.13+)](#error-wrapping-go-113)
- [Topic 9: Interfaces in Go — Deep Dive](#topic-9-interfaces-in-go--deep-dive)
  - [Interface Composition](#interface-composition)
  - [Type Assertion](#type-assertion)
  - [Type Switch](#type-switch)
  - [Stringer Interface](#stringer-interface)
  - [nil Interface](#nil-interface)
  - [Interface vs Concrete Type](#interface-vs-concrete-type)
- [Interview Questions](#interview-questions)

---

## Topic 8: Interfaces & Error Handling

### What is an Interface?

An interface defines a **set of method signatures**. Any type that implements all those methods automatically satisfies the interface — no explicit declaration needed. This is called **implicit implementation**.

```go
// Define an interface
type Shape interface {
    Area() float64
    Perimeter() float64
}

// No "implements Shape" keyword needed — it's automatic!
```

> 💡 Go interfaces are satisfied **implicitly**. If a type has all the methods, it implements the interface. This is different from Java/C# where you explicitly write `implements`.

---

### Implementing an Interface

```go
type Shape interface {
    Area() float64
    Perimeter() float64
}

// Circle implements Shape
type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}

// Rectangle implements Shape
type Rectangle struct {
    Width, Height float64
}

func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

func (r Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}

// Use interface as parameter type
func printShape(s Shape) {
    fmt.Printf("Area: %.2f, Perimeter: %.2f\n", s.Area(), s.Perimeter())
}

c := Circle{Radius: 5}
r := Rectangle{Width: 4, Height: 6}

printShape(c)   // works — Circle has both methods
printShape(r)   // works — Rectangle has both methods
```

---

### Interface with Multiple Types

```go
// Polymorphism — one function works with many types
func totalArea(shapes []Shape) float64 {
    total := 0.0
    for _, s := range shapes {
        total += s.Area()
    }
    return total
}

shapes := []Shape{
    Circle{Radius: 3},
    Rectangle{Width: 4, Height: 5},
    Circle{Radius: 7},
}

fmt.Printf("Total area: %.2f\n", totalArea(shapes))
```

---

### Empty Interface

```go
// interface{} or any — accepts ANY type
// any is alias for interface{} (Go 1.18+)

func printAnything(val interface{}) {
    fmt.Printf("Value: %v, Type: %T\n", val, val)
}

printAnything(42)
printAnything("hello")
printAnything(true)
printAnything([]int{1, 2, 3})

// Commonly used in:
// - fmt.Println(a ...any)
// - json.Unmarshal → map[string]interface{}
// - storing mixed-type data

data := map[string]interface{}{
    "name": "Rahul",
    "age":  25,
    "pass": true,
}
```

---

### Error Handling

```go
// error is a built-in interface
// type error interface {
//     Error() string
// }

// Always check errors immediately
file, err := os.Open("file.txt")
if err != nil {
    fmt.Println("Error:", err)
    return
}
defer file.Close()

// fmt.Errorf — create error with message
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("cannot divide %.2f by zero", a)
    }
    return a / b, nil
}

// errors.New — simple error message
import "errors"
var ErrNotFound = errors.New("item not found")

// Multiple error checks
val, err := step1()
if err != nil { return err }

result, err := step2(val)
if err != nil { return err }
```

---

### Custom Errors

```go
// Create a custom error type by implementing the error interface
type ValidationError struct {
    Field   string
    Message string
}

// Implement Error() string → satisfies error interface
func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error: field '%s' — %s", e.Field, e.Message)
}

// Use custom error
func validateAge(age int) error {
    if age < 0 {
        return &ValidationError{Field: "age", Message: "cannot be negative"}
    }
    if age > 150 {
        return &ValidationError{Field: "age", Message: "unrealistic value"}
    }
    return nil
}

err := validateAge(-5)
if err != nil {
    fmt.Println(err)
    // "validation error: field 'age' — cannot be negative"
}
```

---

### Error Wrapping (Go 1.13+)

```go
import "errors"

// Wrap error with context using %w
func readConfig(path string) error {
    _, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("readConfig: %w", err)  // wrap!
    }
    return nil
}

// errors.Is — checks if error matches target (including wrapped)
var ErrNotFound = errors.New("not found")

err := fmt.Errorf("db query failed: %w", ErrNotFound)
fmt.Println(errors.Is(err, ErrNotFound))   // true

// errors.As — extract specific error type from wrapped error
var valErr *ValidationError
if errors.As(err, &valErr) {
    fmt.Println("Field:", valErr.Field)
}
```

---

## Topic 9: Interfaces in Go — Deep Dive

### Interface Composition

```go
// Interfaces can embed other interfaces
type Reader interface {
    Read() string
}

type Writer interface {
    Write(s string)
}

// ReadWriter embeds both
type ReadWriter interface {
    Reader
    Writer
}

// Standard library examples:
// io.Reader, io.Writer, io.ReadWriter
// io.Closer, io.ReadCloser, io.WriteCloser
```

---

### Type Assertion

```go
// Extract the concrete type from an interface
var s Shape = Circle{Radius: 5}

// Single return — panics if wrong type
c := s.(Circle)
fmt.Println(c.Radius)   // 5

// Safe two-return form — never panics
c, ok := s.(Circle)
if ok {
    fmt.Println("Is Circle, radius:", c.Radius)
} else {
    fmt.Println("Not a Circle")
}

// Wrong type assertion
r, ok := s.(Rectangle)
fmt.Println(ok)   // false — safe, no panic
```

---

### Type Switch

```go
// Most idiomatic way to handle multiple types
func describe(i interface{}) string {
    switch v := i.(type) {
    case int:
        return fmt.Sprintf("int: %d, doubled: %d", v, v*2)
    case string:
        return fmt.Sprintf("string: %q, length: %d", v, len(v))
    case bool:
        return fmt.Sprintf("bool: %t, flipped: %t", v, !v)
    case []int:
        return fmt.Sprintf("[]int with %d elements", len(v))
    case nil:
        return "nil value"
    default:
        return fmt.Sprintf("unknown type: %T", v)
    }
}

fmt.Println(describe(42))
fmt.Println(describe("Go"))
fmt.Println(describe(true))
```

---

### Stringer Interface

```go
// fmt.Stringer — most commonly used interface in Go
// type Stringer interface {
//     String() string
// }

type Person struct {
    Name string
    Age  int
}

// Implement String() → fmt.Println auto-calls it!
func (p Person) String() string {
    return fmt.Sprintf("%s (age %d)", p.Name, p.Age)
}

p := Person{Name: "Rahul", Age: 25}
fmt.Println(p)           // Rahul (age 25)
fmt.Printf("%v\n", p)   // Rahul (age 25)
fmt.Printf("%s\n", p)   // Rahul (age 25)
```

---

### nil Interface

```go
// Interface has two components: (type, value)
// A nil interface has both as nil

var s Shape   // nil interface — type=nil, value=nil
fmt.Println(s == nil)   // true

// TRAP: interface holding nil pointer is NOT nil!
var c *Circle = nil
var s2 Shape = c      // type=*Circle, value=nil
fmt.Println(s2 == nil)  // false ← COMMON INTERVIEW TRAP!
fmt.Println(c == nil)   // true

// Always return nil interface, not nil pointer
func getShape(isCircle bool) Shape {
    if !isCircle {
        return nil        // ✅ nil interface
    }
    return Circle{Radius: 5}
}
```

---

### Interface vs Concrete Type

```go
// When to use interface vs concrete type:

// ✅ USE interface when:
// - Function accepts multiple types
// - You want polymorphism
// - Writing reusable library code
// - Mocking in tests

// ✅ USE concrete type when:
// - Only one type will ever be used
// - Performance is critical (interfaces have small overhead)
// - Internal code not meant to be extended

// Real world: io.Reader is interface
// Accepts: os.File, bytes.Buffer, strings.Reader, http.Response.Body
func processData(r io.Reader) {
    data, _ := io.ReadAll(r)
    fmt.Println(string(data))
}
// Works with ANY type that has Read() method!
```

---

## Interview Questions

### Topic 8: Interfaces & Error Handling

**Q: How does Go implement interfaces? Is it explicit or implicit?**
> Implicit. Any type that has all the methods of an interface automatically satisfies it — no `implements` keyword needed. If a type has `Area() float64` and `Perimeter() float64`, it implements the Shape interface without declaring it.

**Q: What is the error interface in Go?**
> `error` is a built-in interface with one method: `Error() string`. Any type that implements this method is an error. Use `fmt.Errorf` to create simple errors and define custom structs for rich error types.

**Q: How do you create a custom error type?**
> Create a struct and implement the `Error() string` method. Example: `type ValidationError struct { Field, Message string }` with `func (e *ValidationError) Error() string { return ... }`. This makes it satisfy the error interface.

**Q: What is the difference between errors.Is and errors.As?**
> `errors.Is` checks if an error in the chain matches a specific error value (like a sentinel error). `errors.As` extracts a specific error type from the chain. Use `%w` in `fmt.Errorf` to wrap errors so both functions can unwrap the chain.

**Q: What is the empty interface and when do you use it?**
> `interface{}` (or `any` in Go 1.18+) accepts any type since every type has at least zero methods. Used for truly generic containers, JSON unmarshaling, and functions that accept mixed types. Requires type assertion or type switch to get the concrete value back.

---

### Topic 9: Interfaces — Deep Dive

**Q: What is a type assertion in Go?**
> Extracts the concrete type from an interface: `c := s.(Circle)`. Single-return form panics if wrong type. Two-return form `c, ok := s.(Circle)` is safe — ok is false if type doesn't match. Always use the two-return form unless you're certain of the type.

**Q: What is a type switch?**
> A switch statement that checks the dynamic type of an interface: `switch v := i.(type) { case int: ... case string: ... }`. The idiomatic Go way to handle values of unknown type, much cleaner than multiple type assertions.

**Q: What is the Stringer interface?**
> `fmt.Stringer` has one method: `String() string`. When you implement this on a type, `fmt.Println` automatically calls it. Used to give custom string representation to your types — like toString() in Java.

**Q: What is the nil interface trap in Go?**
> An interface has two components: type and value. A nil pointer stored in an interface is NOT a nil interface — the type field is still set. `var c *Circle = nil; var s Shape = c` — here `s == nil` is `false` even though c is nil. Return `nil` directly, not a nil pointer, to get a true nil interface.

**Q: What is interface composition?**
> Interfaces can embed other interfaces. `type ReadWriter interface { Reader; Writer }` means ReadWriter requires all methods of both Reader and Writer. The Go standard library uses this extensively: `io.ReadWriter`, `io.ReadCloser`, `io.ReadWriteCloser`.

**Q: When should you use an interface vs a concrete type?**
> Use interface when a function needs to work with multiple types (polymorphism), for testability (mocking), or in library code. Use concrete types for internal code with a single implementation or where performance is critical. The Go proverb: "Accept interfaces, return concrete types."

---

## Quick Reference

```go
// ── INTERFACE ──────────────────────────────────────────
type Shape interface {
    Area() float64
    Perimeter() float64
}

// Implicit implementation — no keyword needed
func (c Circle) Area() float64 { return math.Pi * c.Radius * c.Radius }

// Use as parameter
func printShape(s Shape) { fmt.Println(s.Area()) }

// Empty interface
func printAny(v interface{}) { fmt.Printf("%v %T\n", v, v) }

// Interface composition
type ReadWriter interface { Reader; Writer }

// ── TYPE ASSERTION ─────────────────────────────────────
c, ok := s.(Circle)     // safe — ok=false if wrong type
c    := s.(Circle)      // unsafe — panics if wrong type

// ── TYPE SWITCH ────────────────────────────────────────
switch v := i.(type) {
case int:    fmt.Println("int:", v)
case string: fmt.Println("string:", v)
default:     fmt.Printf("other: %T\n", v)
}

// ── ERRORS ─────────────────────────────────────────────
errors.New("message")                    // simple error
fmt.Errorf("context: %w", err)          // wrap error
errors.Is(err, ErrNotFound)             // check error chain
errors.As(err, &valErr)                 // extract error type

// Custom error
type MyError struct{ Code int; Msg string }
func (e *MyError) Error() string { return fmt.Sprintf("[%d] %s", e.Code, e.Msg) }

// Stringer
func (p Person) String() string { return fmt.Sprintf("%s(%d)", p.Name, p.Age) }
```

---

## Resources

- [Official Go Documentation](https://go.dev/doc/)
- [Go Tour — Interfaces](https://go.dev/tour/methods/9)
- [Go Playground](https://go.dev/play/)
- [Effective Go — Interfaces](https://go.dev/doc/effective_go#interfaces)

---

*Phase 1 — Days 1-7 | Topics 8 & 9 — COMPLETE ✅*