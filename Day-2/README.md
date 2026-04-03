# 🐹 Go Language — Phase 1 Study Notes (Days 1–7)

> Complete notes for **Topic 3: Short Variable Declaration & Type Inference**, **Topic 4: Go Language Basics Part 2**, **Topic 5: Control Structures (if, switch, loops)**
> Prepared for interview revision and quick reference.

---

## 📚 Table of Contents

- [Topic 3: Short Variable Declaration & Type Inference](#topic-3-short-variable-declaration--type-inference)
- [Topic 4: Go Language Basics Part 2](#topic-4-go-language-basics-part-2)
- [Topic 5: Control Structures](#topic-5-control-structures)
  - [if / else if / else](#if--else-if--else)
  - [switch](#switch)
  - [for loop — all 3 forms](#for-loop--all-3-forms)
  - [range](#range)
  - [break, continue, goto](#break-continue-goto)
- [Interview Questions](#interview-questions)

---

## Topic 3: Short Variable Declaration & Type Inference

### Short Variable Declaration — `:=`

```go
// := declares AND assigns in one step
name := "Rahul"       // type inferred as string
age  := 25            // type inferred as int
gpa  := 8.5           // type inferred as float64
pass := true          // type inferred as bool
```

### Rules of `:=`

```go
// ✅ Rule 1: Only inside functions
func main() {
    x := 10   // fine
}
// x := 10   // package level = compile error ❌

// ✅ Rule 2: At least one NEW variable on left side
a, b := 1, 2       // both new — fine ✅
a, c := 3, 4       // a already exists, c is new — fine ✅
// a, b := 5, 6   // both exist — compile error ❌

// ✅ Rule 3: Cannot use := with explicit type
// x int := 10   // syntax error ❌
var x int = 10    // correct ✅
```

### Type Inference — How Go decides the type

```go
x   := 42          // int      (default for whole numbers)
y   := 3.14        // float64  (default for decimals)
z   := "hello"     // string
b   := true        // bool
r   := 'A'         // int32 / rune
c   := 2 + 3i      // complex128

// Check inferred type
fmt.Printf("%T\n", x)   // int
fmt.Printf("%T\n", y)   // float64
fmt.Printf("%T\n", r)   // int32
```

> 📌 Go always infers the **widest safe type** — untyped int literals become `int`, decimals become `float64`. Never `int32` or `float32` by default.

### Type Inference with Expressions

```go
a := 10             // int
b := 3.14           // float64
// c := a + b       // compile error! int + float64 ❌

c := float64(a) + b // must convert explicitly ✅

// Function return type is inferred
result := math.Sqrt(16)   // float64 (whatever Sqrt returns)
length := len("hello")    // int     (whatever len returns)
```

### Blank Identifier `_`

```go
// Ignore values you don't need using _
val, _ := strconv.Atoi("42")    // ignore the error

// Ignore loop index
for _, v := range []int{1, 2, 3} {
    fmt.Println(v)
}

// _ is write-only — you cannot read from it
// fmt.Println(_)  // compile error ❌
```

---

## Topic 4: Go Language Basics Part 2

### Multiple Return Values

```go
// Functions can return multiple values — unique to Go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("cannot divide by zero")
    }
    return a / b, nil
}

// Caller must handle both
result, err := divide(10, 2)
if err != nil {
    fmt.Println("Error:", err)
} else {
    fmt.Println(result)   // 5
}

// Ignore one with _
result, _ := divide(10, 2)
```

### Named Return Values

```go
// Name the return variables directly in signature
func minMax(nums []int) (min int, max int) {
    min, max = nums[0], nums[0]
    for _, n := range nums {
        if n < min { min = n }
        if n > max { max = n }
    }
    return   // "naked return" — returns min and max
}

result_min, result_max := minMax([]int{3, 1, 9, 2})
fmt.Println(result_min, result_max)  // 1 9
```

### Variadic Functions

```go
// Accept any number of arguments with ...
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

fmt.Println(sum(1, 2, 3))          // 6
fmt.Println(sum(1, 2, 3, 4, 5))    // 15

// Spread a slice into variadic function
nums := []int{1, 2, 3, 4}
fmt.Println(sum(nums...))           // 10
```

### init() Function

```go
// init() runs automatically before main()
// Used for setup: config, DB connections, etc.
var config string

func init() {
    config = "loaded"
    fmt.Println("init() ran first")
}

func main() {
    fmt.Println("main() ran second")
    fmt.Println(config)   // "loaded"
}
// Output:
// init() ran first
// main() ran second
// loaded
```

### defer

```go
// defer runs the statement AFTER the surrounding function returns
func main() {
    defer fmt.Println("3 - deferred, runs last")
    fmt.Println("1 - runs first")
    fmt.Println("2 - runs second")
}
// Output: 1 → 2 → 3

// Multiple defers run in LIFO order (last in, first out)
func main() {
    defer fmt.Println("first defer")   // runs last
    defer fmt.Println("second defer")  // runs second
    defer fmt.Println("third defer")   // runs first
    fmt.Println("main body")
}
// Output: main body → third defer → second defer → first defer
```

> 💡 `defer` is commonly used for cleanup: closing files, releasing locks, closing DB connections.

---

## Topic 5: Control Structures

### if / else if / else

```go
// Basic if-else
score := 85

if score >= 90 {
    fmt.Println("A grade")
} else if score >= 75 {
    fmt.Println("B grade")
} else if score >= 60 {
    fmt.Println("C grade")
} else {
    fmt.Println("Fail")
}

// if with init statement — variable scoped to if block
if val, err := strconv.Atoi("42"); err == nil {
    fmt.Println("Parsed:", val)   // val only exists inside this if
} else {
    fmt.Println("Error:", err)
}
// fmt.Println(val)   // compile error — val not in scope here ❌
```

> 📌 No parentheses `()` around condition in Go. Braces `{}` are mandatory.

### switch

```go
// Basic switch — no fallthrough by default
day := "Monday"
switch day {
case "Saturday", "Sunday":
    fmt.Println("Weekend")
case "Monday", "Tuesday", "Wednesday", "Thursday", "Friday":
    fmt.Println("Weekday")
default:
    fmt.Println("Unknown")
}

// Switch with no condition (acts like if-else chain)
score := 78
switch {
case score >= 90:
    fmt.Println("A")
case score >= 75:
    fmt.Println("B")   // prints this
default:
    fmt.Println("C")
}

// Switch with init statement
switch os := runtime.GOOS; os {
case "darwin":
    fmt.Println("Mac")
case "linux":
    fmt.Println("Linux")
default:
    fmt.Println("Other:", os)
}

// fallthrough — explicitly continue to next case
switch 2 {
case 1:
    fmt.Println("one")
case 2:
    fmt.Println("two")
    fallthrough          // executes next case too
case 3:
    fmt.Println("three") // this runs too
case 4:
    fmt.Println("four")  // this does NOT run
}
// Output: two → three
```

### for Loop — All 3 Forms

```go
// Form 1: Classic C-style for loop
for i := 0; i < 5; i++ {
    fmt.Println(i)   // 0 1 2 3 4
}

// Form 2: while-style (condition only)
n := 1
for n < 100 {
    n *= 2
}
fmt.Println(n)   // 128

// Form 3: infinite loop
for {
    fmt.Println("running")
    break   // need break to exit
}
```

> 📌 Go has **only one loop keyword** — `for`. There is no `while` or `do-while`.

### range

```go
// range over slice — gives index and value
nums := []int{10, 20, 30, 40}
for i, v := range nums {
    fmt.Printf("index:%d value:%d\n", i, v)
}

// range over string — gives rune index and rune (not byte!)
for i, r := range "Hello, 世界" {
    fmt.Printf("%d: %c\n", i, r)
}

// range over map — gives key and value
m := map[string]int{"a": 1, "b": 2}
for k, v := range m {
    fmt.Printf("%s → %d\n", k, v)
}

// Ignore index or value with _
for _, v := range nums { fmt.Println(v) }   // only value
for i := range nums    { fmt.Println(i) }   // only index
```

### break, continue, goto

```go
// break — exit loop immediately
for i := 0; i < 10; i++ {
    if i == 5 {
        break   // stops at 5
    }
    fmt.Println(i)   // 0 1 2 3 4
}

// continue — skip current iteration
for i := 0; i < 10; i++ {
    if i%2 == 0 {
        continue   // skip even numbers
    }
    fmt.Println(i)   // 1 3 5 7 9
}

// Labeled break — break out of outer loop
outer:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if i == 1 && j == 1 {
            break outer   // breaks BOTH loops
        }
        fmt.Printf("%d,%d ", i, j)
    }
}
// Output: 0,0 0,1 0,2 1,0
```

---

## Interview Questions

### Topic 3: Short Variable Declaration & Type Inference

**Q: What is the difference between var and := ?**
> `var` works anywhere — package level and inside functions — and supports explicit types. `:=` works only inside functions, infers the type automatically, and requires at least one new variable on the left side.

**Q: Can you use := at package level?**
> No. `:=` is only valid inside functions. At package level you must use `var`. Trying to use `:=` at package level is a compile error.

**Q: What type does Go infer for 42? For 3.14?**
> `42` is inferred as `int`. `3.14` is inferred as `float64`. Go always picks the widest default type — never `int32` or `float32` by default.

**Q: What is the blank identifier _ used for?**
> `_` discards values you don't need — like the error from a function, or the index in a range loop. You can write to it but never read from it.

**Q: When would := cause a compile error?**
> Two cases: (1) all variables on the left already exist in the same scope — at least one must be new, (2) using it at package level outside any function.

---

### Topic 4: Go Language Basics Part 2

**Q: Can a Go function return multiple values?**
> Yes — this is one of Go's key features. You declare multiple return types in the signature: `func f() (int, error)`. Callers receive all values: `val, err := f()`.

**Q: What are named return values?**
> You can name return variables in the function signature: `func f() (x int, y int)`. Then a bare `return` at the end returns those named variables. Called a "naked return". Useful for short functions.

**Q: What is defer used for?**
> `defer` delays execution of a statement until the surrounding function returns. Used for cleanup — closing files, releasing locks, closing DB connections. Multiple defers run in LIFO order (last deferred runs first).

**Q: What is the difference between defer and a normal call?**
> A normal call runs immediately. A deferred call runs only when the surrounding function exits — whether it returns normally or panics. Arguments to defer are evaluated immediately though, not when it runs.

---

### Topic 5: Control Structures

**Q: Does Go have a while loop?**
> No. Go has only one loop keyword — `for`. You write a while loop as `for condition { }` and an infinite loop as `for { }`.

**Q: Does switch in Go fall through by default?**
> No — the opposite of C/Java. In Go, switch cases do NOT fall through by default. You must explicitly write `fallthrough` to continue to the next case.

**Q: What is the if init statement?**
> Go allows a short statement before the condition in if: `if val, err := f(); err == nil { }`. The variable `val` is scoped only to that if-else block — not available outside.

**Q: What is a labeled break?**
> A labeled break (`break outer`) exits a named outer loop directly, instead of just the innermost loop. Used to escape nested loops without a flag variable.

**Q: What does range return for a string?**
> range on a string returns the byte index and the rune (Unicode character) — not the byte value. This makes range safe for multi-byte characters like Hindi or emoji, unlike direct indexing with `s[i]`.

**Q: Can you use switch without a condition in Go?**
> Yes. `switch { case x > 10: ... }` works like an if-else chain. Each case is evaluated as a boolean expression. This is a cleaner alternative to long if-else if chains.

---

## Quick Reference Cheatsheet

```go
// Short declaration
x := 42           // int
y := 3.14         // float64
a, b := 1, 2      // multiple
_, err := f()     // ignore with _

// if with init
if v, err := f(); err == nil { use(v) }

// switch
switch x {
case 1, 2:  fmt.Println("one or two")
case 3:     fmt.Println("three")
default:    fmt.Println("other")
}

// switch no condition
switch {
case x > 10: fmt.Println("big")
default:     fmt.Println("small")
}

// for — 3 forms
for i := 0; i < n; i++ { }    // classic
for condition { }               // while-style
for { }                         // infinite

// range
for i, v := range slice  { }
for i, r := range string { }   // r is rune!
for k, v := range map    { }

// defer
defer file.Close()    // runs when function exits, LIFO order

// multiple return
func f() (int, error) { return 42, nil }
val, err := f()
```

---

## Resources

- [Official Go Documentation](https://go.dev/doc/)
- [Go Tour — Flow Control](https://go.dev/tour/flowcontrol)
- [Go Playground](https://go.dev/play/)
- [Effective Go](https://go.dev/doc/effective_go)

---

*Phase 1 — Days 1-7 | Topics 3, 4 & 5 covered*