"""
smart_local_engine.py — UPGRADED
──────────────────────────────────
Real knowledge engine. No API keys needed. No "please use ChatGPT" messages.
Covers Python, JavaScript, algorithms, SQL, web, git, Docker, ML, and more.

Response priority in app.py:
  1. FAISS semantic search (8M examples)
  2. Trained DB knowledge
  3. High-rated past answers
  4. THIS ENGINE  ← comprehensive local knowledge
  5. local_llm.py (GGUF model)
"""

import random
import re

# ─────────────────────────────────────────────────────────────
# KNOWLEDGE BASE
# ─────────────────────────────────────────────────────────────

KNOWLEDGE = {
    # ── Python ──────────────────────────────────────────────
    "python list": """**Python Lists** — ordered, mutable collections.

```python
fruits = ["apple", "banana", "cherry"]

# Access
fruits[0]        # "apple"
fruits[-1]       # "cherry" (last)
fruits[1:3]      # ["banana", "cherry"] (slice)

# Modify
fruits.append("date")          # add to end
fruits.insert(1, "avocado")    # insert at index
fruits.remove("banana")        # remove by value
item = fruits.pop()            # remove & return last

# Sort
fruits.sort()                  # in-place, ascending
fruits.sort(reverse=True)      # descending
sorted_list = sorted(fruits)   # returns new list

# List comprehension (fast & Pythonic)
squares  = [x**2 for x in range(10)]
evens    = [x for x in range(20) if x % 2 == 0]
flat     = [n for row in [[1,2],[3,4]] for n in row]

# Useful operations
len(fruits)               # length
"apple" in fruits         # membership check  → True/False
fruits.count("apple")     # count occurrences
fruits.index("cherry")    # first index of value
fruits.reverse()          # reverse in-place
fruits2 = fruits.copy()   # shallow copy
fruits + ["grape"]        # concatenate (returns new list)
```

**Complexity:** O(1) index/append, O(n) search/insert/delete.""",

    "python dict": """**Python Dictionaries** — key-value hash map.

```python
person = {"name": "Alice", "age": 30, "city": "NY"}

# Access
person["name"]                   # "Alice"
person.get("email", "N/A")       # safe: returns default if missing

# Modify
person["age"]   = 31             # update
person["email"] = "a@b.com"      # add key
del person["city"]               # delete key
person.pop("city", None)         # delete + return (safe)

# Iteration
for key in person:               print(key)
for val in person.values():      print(val)
for k, v in person.items():      print(f"{k}: {v}")

# Comprehension
squares = {x: x**2 for x in range(5)}   # {0:0, 1:1, 2:4, ...}

# Merge (Python 3.9+)
merged = dict1 | dict2           # non-destructive
dict1 |= dict2                   # in-place update

# Patterns
# Count words
from collections import Counter
counts = Counter("hello world".split())  # Counter({'hello':1,'world':1})

# Group by
from collections import defaultdict
grouped = defaultdict(list)
for item in data:
    grouped[item["category"]].append(item)

# Check membership
"name" in person        # True
"email" not in person   # True
```

**Complexity:** O(1) average get/set/delete.""",

    "python function": """**Python Functions** — reusable blocks of logic.

```python
# Basic
def greet(name):
    return f"Hello, {name}!"

# Default arguments
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# *args — variable positional
def total(*numbers):
    return sum(numbers)
total(1, 2, 3, 4)    # 10

# **kwargs — variable keyword
def show(**info):
    for k, v in info.items():
        print(f"{k}: {v}")
show(name="Alice", age=30)

# Type hints (Python 3.5+)
def add(a: int, b: int) -> int:
    return a + b

# Lambda (one-liner)
square = lambda x: x ** 2
nums = [3, 1, 4, 1, 5]
nums.sort(key=lambda x: -x)     # sort descending

# Map / Filter / Reduce
doubled = list(map(lambda x: x*2, [1,2,3]))       # [2,4,6]
evens   = list(filter(lambda x: x%2==0, [1..6]))  # [2,4,6]
from functools import reduce
product = reduce(lambda a, b: a*b, [1,2,3,4])     # 24

# Decorator
from functools import wraps
import time

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.perf_counter()-t:.4f}s")
        return result
    return wrapper

@timer
def slow():
    time.sleep(0.5)

# Memoization
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n <= 1 else fib(n-1) + fib(n-2)
```""",

    "python class": """**Python Classes** — object-oriented programming.

```python
class Animal:
    count = 0                      # class variable (shared)

    def __init__(self, name: str, species: str):
        self.name    = name        # instance variable
        self.species = species
        Animal.count += 1

    def speak(self) -> str:        # instance method
        return f"{self.name} makes a sound"

    @classmethod
    def get_count(cls) -> int:     # class method
        return cls.count

    @staticmethod
    def is_animal(obj) -> bool:    # static method (no self)
        return isinstance(obj, Animal)

    def __repr__(self):            # developer-friendly repr
        return f"Animal({self.name!r})"

    def __str__(self):             # user-friendly str
        return self.name

    def __eq__(self, other):       # equality check
        return self.name == other.name

# Inheritance
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name, "Canis lupus")
        self.breed = breed

    def speak(self):               # override
        return f"{self.name}: Woof!"

d = Dog("Rex", "Lab")
print(d.speak())                   # Rex: Woof!
print(isinstance(d, Animal))       # True

# Dataclass (less boilerplate)
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float
    tags: list = field(default_factory=list)

    def distance(self):
        return (self.x**2 + self.y**2) ** 0.5

p = Point(3.0, 4.0)
print(p.distance())   # 5.0
print(p)              # Point(x=3.0, y=4.0, tags=[])
```""",

    "python async": """**Python Async / Await** — non-blocking concurrency.

```python
import asyncio

# Basic async function
async def fetch(url: str) -> str:
    await asyncio.sleep(1)          # simulates network I/O
    return f"data from {url}"

# Run it
asyncio.run(fetch("example.com"))

# Run MULTIPLE tasks in parallel (gather)
async def main():
    # All three run at the same time (~1s total, not 3s)
    a, b, c = await asyncio.gather(
        fetch("site1.com"),
        fetch("site2.com"),
        fetch("site3.com"),
    )
    return a, b, c

# Real HTTP with httpx
import httpx

async def get_users():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://jsonplaceholder.typicode.com/users")
        return r.json()

# Async generator
async def stream_numbers(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def use():
    async for num in stream_numbers(5):
        print(num)

# FastAPI (uses async automatically)
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
async def users():
    return await get_users()

# asyncio.create_task — background task
async def background_worker():
    while True:
        await asyncio.sleep(60)
        print("tick")

async def main():
    task = asyncio.create_task(background_worker())
    await asyncio.sleep(300)
    task.cancel()
```""",

    "python generator": """**Python Generators** — memory-efficient lazy iterators.

```python
# Generator function (uses yield)
def count_up(n):
    for i in range(n):
        yield i            # pause, return value, resume next call

gen = count_up(3)
next(gen)   # 0
next(gen)   # 1
next(gen)   # 2

# In a for loop
for num in count_up(1_000_000):   # uses ~0 memory!
    print(num)

# Generator expression (like list comprehension but lazy)
squares_lazy = (x**2 for x in range(1_000_000))  # ~100 bytes
squares_list = [x**2 for x in range(1_000_000)]  # ~8 MB

# Read huge file line-by-line (no memory overload)
def read_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

# yield from — delegate to sub-generator
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

list(flatten([1, [2, [3, 4]], 5]))   # [1, 2, 3, 4, 5]

# Pipeline pattern
def read(path):       yield from open(path)
def filter_empty(it): yield from (l for l in it if l.strip())
def to_upper(it):     yield from (l.upper() for l in it)

for line in to_upper(filter_empty(read("data.txt"))):
    print(line)
```""",

    # ── Algorithms ──────────────────────────────────────────
    "binary search": """**Binary Search** — O(log n) search in sorted data.

```python
# Iterative (preferred)
def binary_search(arr: list, target) -> int:
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:   return mid        # found
        elif arr[mid] < target:  left  = mid + 1   # go right
        else:                    right = mid - 1   # go left
    return -1   # not found

# Python's bisect (fastest, built-in)
from bisect import bisect_left

def binary_search_fast(arr, target):
    i = bisect_left(arr, target)
    return i if i < len(arr) and arr[i] == target else -1

# Find insertion position
from bisect import insort
arr = [1, 3, 5, 7]
insort(arr, 4)    # arr = [1, 3, 4, 5, 7]

# Usage
arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
binary_search(arr, 7)    #  3
binary_search(arr, 6)    # -1
binary_search(arr, 19)   #  9
```

**Why it's fast:**
A sorted list of 1 **billion** items takes at most **30 comparisons**.
Linear search could take 1 billion. That's the power of O(log n).""",

    "sorting": """**Sorting Algorithms** — which one to use when.

```python
# Always use this in Python (Timsort, O(n log n), stable)
data = [3, 1, 4, 1, 5, 9, 2, 6]
data.sort()                              # in-place
sorted_data = sorted(data)              # new list
data.sort(key=lambda x: -x)            # descending
people.sort(key=lambda p: p["age"])    # sort by field
people.sort(key=lambda p: (p["age"], p["name"]))  # multi-key

# MERGE SORT — O(n log n), stable, great for linked lists
def merge_sort(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    L, R = merge_sort(arr[:mid]), merge_sort(arr[mid:])
    result, i, j = [], 0, 0
    while i < len(L) and j < len(R):
        if L[i] <= R[j]: result.append(L[i]); i += 1
        else:             result.append(R[j]); j += 1
    return result + L[i:] + R[j:]

# QUICK SORT — O(n log n) avg, fastest in practice
def quick_sort(arr):
    if len(arr) <= 1: return arr
    pivot = arr[len(arr) // 2]
    left  = [x for x in arr if x < pivot]
    mid   = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)

# HEAP SORT — O(n log n), in-place, not stable
import heapq
def heap_sort(arr):
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]
```

| Algorithm | Time | Space | Stable | Use when |
|-----------|------|-------|--------|----------|
| Python sort() | O(n log n) | O(n) | ✅ | Always |
| Merge sort | O(n log n) | O(n) | ✅ | Linked lists |
| Quick sort | O(n log n) | O(log n) | ❌ | General |
| Heap sort | O(n log n) | O(1) | ❌ | Memory constrained |
| Bubble sort | O(n²) | O(1) | ✅ | Never in production |""",

    "recursion": """**Recursion** — solving problems by breaking them down.

```python
# Factorial — classic recursion
def factorial(n: int) -> int:
    if n <= 1: return 1           # base case (MUST exist)
    return n * factorial(n - 1)   # recursive case

factorial(5)  # 120

# Fibonacci — memoized (fast)
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

fib(50)   # instant with memoization

# Flatten nested list
def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

flatten([1, [2, [3, 4]], 5])   # [1, 2, 3, 4, 5]

# Binary tree traversal
class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def inorder(root):    # Left → Root → Right
    if not root: return []
    return inorder(root.left) + [root.val] + inorder(root.right)

# Power set
def power_set(s):
    if not s: return [[]]
    rest = power_set(s[1:])
    return rest + [[s[0]] + sub for sub in rest]

power_set([1,2,3])  # [[], [1], [2], [1,2], [3], [1,3], [2,3], [1,2,3]]
```

**Rules:** always define a base case, move toward it each call, use `@lru_cache` for overlapping subproblems.""",

    "dynamic programming": """**Dynamic Programming** — remember subproblem solutions.

```python
# Fibonacci (bottom-up)
def fib(n):
    if n <= 1: return n
    dp = [0, 1] + [0] * (n - 1)
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# Coin Change — min coins to make amount
def coin_change(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

coin_change([1, 5, 10, 25], 36)   # 3  (25+10+1)

# Longest Common Subsequence
def lcs(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    dp = [[0] * (n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1] + 1
            else:                   dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]

lcs("ABCBDAB", "BDCABA")   # 4

# 0/1 Knapsack
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for w in range(capacity+1):
            dp[i][w] = dp[i-1][w]
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w-weights[i-1]] + values[i-1])
    return dp[n][capacity]
```

**Pattern:** define state → write recurrence → fill table bottom-up or use `@lru_cache` top-down.""",

    "big o": """**Big O Notation** — algorithm complexity cheatsheet.

| Notation | Name | Example | n=1000 |
|----------|------|---------|--------|
| O(1) | Constant | dict lookup, array index | 1 op |
| O(log n) | Logarithmic | binary search | 10 ops |
| O(n) | Linear | linear scan | 1,000 ops |
| O(n log n) | Linearithmic | merge sort | 10,000 ops |
| O(n²) | Quadratic | nested loops | 1,000,000 ops |
| O(2ⁿ) | Exponential | brute-force subsets | astronomical |

```python
# O(1) — constant (doesn't grow with input)
d = {"a": 1}
x = d["a"]           # O(1)
arr = [1, 2, 3]
x = arr[0]           # O(1)

# O(n) — linear
def find(arr, t):
    for x in arr:    # n iterations
        if x == t: return True
    return False

# O(n²) — quadratic (bad for large n)
def has_dupe_slow(arr):
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):   # nested!
            if arr[i] == arr[j]: return True
    return False

# O(n) — same problem, smarter
def has_dupe_fast(arr):
    return len(arr) != len(set(arr))   # set lookup = O(1)

# O(log n) — binary search
def bsearch(arr, t):
    l, r = 0, len(arr)-1
    while l <= r:
        m = (l+r)//2
        if arr[m]==t: return m
        elif arr[m]<t: l=m+1
        else: r=m-1
    return -1
```

**Space complexity** works the same way — O(n) space = memory grows proportionally.""",

    # ── JavaScript ──────────────────────────────────────────
    "javascript promise": """**JavaScript Promises & async/await** — handle async code cleanly.

```javascript
// Create a promise
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// async/await (cleanest syntax)
async function fetchUser(id) {
    try {
        const res = await fetch(`/api/users/${id}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error("Failed:", err.message);
        return null;
    }
}

// Parallel (all at once, ~1s not 3s)
async function loadAll() {
    const [users, posts] = await Promise.all([
        fetch("/api/users").then(r => r.json()),
        fetch("/api/posts").then(r => r.json()),
    ]);
    return { users, posts };
}

// First one wins
const fastest = await Promise.race([
    fetch("/api/server1").then(r => r.json()),
    fetch("/api/server2").then(r => r.json()),
]);

// All settle (won't fail if one rejects)
const results = await Promise.allSettled([
    fetch("/api/a").then(r => r.json()),
    fetch("/api/b").then(r => r.json()),
]);
results.forEach(r => {
    if (r.status === "fulfilled") console.log(r.value);
    else console.error(r.reason);
});

// .then() chaining
fetch("/api/users")
    .then(r  => r.json())
    .then(us => us.filter(u => u.active))
    .then(console.log)
    .catch(console.error)
    .finally(() => console.log("done"));
```""",

    "javascript closure": """**JavaScript Closures** — functions that remember their scope.

```javascript
// Counter with private state
function makeCounter(initial = 0) {
    let count = initial;   // private — not accessible outside
    return {
        increment() { count++; },
        decrement() { count--; },
        reset()     { count = initial; },
        value()     { return count; },
    };
}
const c = makeCounter(10);
c.increment(); c.increment();
c.value();   // 12

// Factory with closure
const multiplier = factor => n => n * factor;
const double = multiplier(2);
const triple = multiplier(3);
double(5);   // 10
triple(5);   // 15

// Memoize with closure
function memoize(fn) {
    const cache = new Map();
    return function(...args) {
        const key = JSON.stringify(args);
        if (cache.has(key)) return cache.get(key);
        const result = fn(...args);
        cache.set(key, result);
        return result;
    };
}
const expensiveFn = memoize(n => n * n);

// Module pattern (private + public)
const BankAccount = (function() {
    let _balance = 0;   // private
    return {
        deposit(n)  { if (n > 0) _balance += n; },
        withdraw(n) { if (n <= _balance) _balance -= n; },
        balance()   { return _balance; },
    };
})();
BankAccount.deposit(100);
BankAccount.balance();   // 100
```""",

    "javascript array": """**JavaScript Array Methods** — functional style.

```javascript
const nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// map — transform each element → new array
const doubled = nums.map(n => n * 2);    // [2,4,6,...,20]

// filter — keep matching elements → new array
const evens = nums.filter(n => n % 2 === 0);  // [2,4,6,8,10]

// reduce — collapse to single value
const sum = nums.reduce((acc, n) => acc + n, 0);  // 55

// find / findIndex — first match
const first  = nums.find(n => n > 7);       // 8
const idx    = nums.findIndex(n => n > 7);  // 7

// every / some
const allPos = nums.every(n => n > 0);   // true
const hasNeg = nums.some(n => n < 0);    // false

// flat / flatMap
[[1,2],[3,4]].flat();                    // [1,2,3,4]
["a b", "c d"].flatMap(s => s.split(" "));  // ["a","b","c","d"]

// includes
nums.includes(5);   // true

// Chaining (most powerful)
const result = nums
    .filter(n => n % 2 === 0)    // [2,4,6,8,10]
    .map(n => n ** 2)             // [4,16,36,64,100]
    .reduce((s, n) => s + n, 0); // 220

// Spread & destructuring
const [first, second, ...rest] = nums;
const combined = [...nums, 11, 12];

// Sort (mutates! — copy first)
[...nums].sort((a, b) => b - a);  // descending
people.sort((a, b) => a.name.localeCompare(b.name));
```""",

    # ── Web Dev ─────────────────────────────────────────────
    "html": """**HTML Essentials** — web page structure.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Page</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
        </nav>
    </header>

    <main>
        <h1>Heading 1</h1>
        <h2>Heading 2</h2>
        <p>Paragraph with <strong>bold</strong>, <em>italic</em>, <code>code</code>.</p>

        <!-- Image -->
        <img src="photo.jpg" alt="A description" width="400">

        <!-- Lists -->
        <ul><li>Unordered</li></ul>
        <ol><li>Ordered</li></ol>

        <!-- Form -->
        <form action="/submit" method="POST">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" required>

            <label for="email">Email</label>
            <input type="email" id="email" name="email">

            <select name="role">
                <option value="user">User</option>
                <option value="admin">Admin</option>
            </select>

            <textarea name="bio" rows="4"></textarea>

            <button type="submit">Submit</button>
        </form>

        <!-- Table -->
        <table>
            <thead><tr><th>Name</th><th>Age</th></tr></thead>
            <tbody><tr><td>Alice</td><td>30</td></tr></tbody>
        </table>
    </main>

    <footer><p>&copy; 2025</p></footer>
    <script src="app.js"></script>
</body>
</html>
```""",

    "css": """**CSS Essentials** — style and layout.

```css
/* Selectors */
h1          { color: #1f2937; }         /* element */
.card       { background: white; }      /* class */
#hero       { height: 100vh; }          /* id */
a:hover     { color: #3b82f6; }         /* pseudo-class */

/* Box model */
.box {
    width: 300px;
    padding: 16px;          /* inner space */
    border: 1px solid #ccc;
    margin: 12px auto;      /* outer space, centered */
    box-sizing: border-box; /* include padding in width */
}

/* Flexbox — 1D layout */
.flex {
    display: flex;
    justify-content: space-between;  /* horizontal */
    align-items: center;             /* vertical */
    flex-wrap: wrap;
    gap: 16px;
}
.flex-item { flex: 1; }   /* equal width */

/* Grid — 2D layout */
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}
.span-full { grid-column: 1 / -1; }   /* full width */

/* Responsive */
@media (max-width: 768px) {
    .grid { grid-template-columns: 1fr; }
}

/* Variables */
:root {
    --primary: #3b82f6;
    --text: #1f2937;
    --radius: 8px;
}
.button { background: var(--primary); border-radius: var(--radius); }

/* Animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.card { animation: fadeIn 0.3s ease-out; }

/* Transition */
.button {
    transition: all 0.2s ease;
}
.button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
```""",

    "rest api": """**REST API** — design and implementation.

```python
# FastAPI (Python) — full CRUD
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

db = {}
next_id = 1

@app.get("/users")
async def list_users():
    return list(db.values())

@app.get("/users/{uid}")
async def get_user(uid: int):
    if uid not in db:
        raise HTTPException(404, "User not found")
    return db[uid]

@app.post("/users", status_code=201)
async def create_user(user: User):
    global next_id
    db[next_id] = {"id": next_id, **user.dict()}
    next_id += 1
    return db[next_id - 1]

@app.put("/users/{uid}")
async def update_user(uid: int, user: User):
    if uid not in db:
        raise HTTPException(404, "User not found")
    db[uid] = {"id": uid, **user.dict()}
    return db[uid]

@app.delete("/users/{uid}", status_code=204)
async def delete_user(uid: int):
    db.pop(uid, None)
```

**HTTP methods:** GET=read, POST=create, PUT=replace, PATCH=partial update, DELETE=remove

**Status codes:**
- 200 OK, 201 Created, 204 No Content
- 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found
- 500 Internal Server Error""",

    # ── SQL ─────────────────────────────────────────────────
    "sql": """**SQL Essentials** — querying databases.

```sql
-- SELECT
SELECT name, email FROM users WHERE active = 1 ORDER BY name LIMIT 10;

-- INSERT
INSERT INTO users (name, email) VALUES ('Alice', 'a@b.com');

-- UPDATE
UPDATE users SET age = 31 WHERE id = 1;

-- DELETE
DELETE FROM users WHERE active = 0;

-- Filtering
SELECT * FROM users
WHERE age BETWEEN 18 AND 65
  AND city IN ('NY', 'LA')
  AND name LIKE 'A%'
  AND email IS NOT NULL;

-- JOINS
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id;       -- inner join

SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;  -- all users, even without orders

-- Aggregate + GROUP BY
SELECT city, COUNT(*) as cnt, AVG(age) as avg_age
FROM users
GROUP BY city
HAVING COUNT(*) > 5
ORDER BY cnt DESC;

-- Subquery
SELECT name FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 100);

-- CTE (Common Table Expression)
WITH active AS (SELECT * FROM users WHERE active = 1)
SELECT * FROM active WHERE age > 25;

-- Window function
SELECT name, salary,
    RANK() OVER (PARTITION BY dept ORDER BY salary DESC) as rank
FROM employees;
```""",

    # ── Git ─────────────────────────────────────────────────
    "git": """**Git Commands** — version control essentials.

```bash
# Setup
git config --global user.name "Your Name"
git config --global user.email "you@email.com"

# Start
git init                    # new repo
git clone <url>             # copy existing

# Daily workflow
git status                  # see what changed
git diff                    # see line changes
git add file.py             # stage file
git add .                   # stage everything
git commit -m "feat: add login"   # save snapshot

# Branches
git branch                  # list branches
git checkout -b feature/x   # create + switch
git merge feature/x         # merge into current
git branch -d feature/x     # delete

# Remote
git push origin main        # upload
git pull origin main        # download + merge
git fetch                   # download only (safe)

# Undo
git restore file.py         # discard unstaged changes
git reset HEAD~1            # undo last commit (keep files)
git reset --hard HEAD~1     # undo last commit (lose files)
git revert <hash>           # safe undo (adds new commit)

# History
git log --oneline --graph   # visual history
git show <hash>             # inspect a commit
git blame file.py           # who changed each line

# Stash
git stash                   # save work-in-progress
git stash pop               # restore it

# Tags
git tag v1.0.0              # tag current commit
git push origin --tags      # push tags
```

**Good commit messages:**
```
feat: add user authentication
fix: correct email validation
refactor: simplify DB queries
docs: update README
```""",

    # ── Docker ──────────────────────────────────────────────
    "docker": """**Docker** — containerize applications.

```dockerfile
# Dockerfile (Python app)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on: [db]
    volumes: [./static:/app/static]

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes: [pgdata:/var/lib/postgresql/data]

volumes:
  pgdata:
```

```bash
# Build & run
docker build -t myapp .
docker run -p 8000:8000 myapp

# Compose
docker-compose up -d          # start background
docker-compose down           # stop
docker-compose logs -f web    # follow logs

# Inspect
docker ps                     # running containers
docker exec -it <id> bash     # open shell in container
docker logs <id>              # view logs
docker inspect <id>           # full details
docker stats                  # live resource usage

# Images
docker images                 # list
docker pull nginx:alpine      # download
docker rmi myapp              # delete
```""",

    # ── ML/AI ───────────────────────────────────────────────
    "machine learning": """**Machine Learning Basics** — core concepts.

**Types:**
1. **Supervised** — labeled data → predictions (regression/classification)
2. **Unsupervised** — unlabeled data → clusters/patterns
3. **Reinforcement** — agent + rewards → policy (games, robotics)

```python
# scikit-learn quick start
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

# 1. Prepare data
X = np.random.rand(200, 4)
y = (X[:, 0] + X[:, 1] > 1).astype(int)

# 2. Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Scale features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)    # use same scaler!

# 4. Train
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Evaluate
preds = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
print(classification_report(y_test, preds))

# 6. Predict new data
new = scaler.transform([[0.8, 0.7, 0.3, 0.4]])
model.predict(new)   # [1] or [0]
```

**Key concepts:**
- **Overfitting** — memorizes training data, fails on new → use regularization, more data
- **Underfitting** — too simple → more features, complex model
- **Cross-validation** — more reliable evaluation than single train/test split
- **Feature scaling** — required for SVM, KNN, neural nets; not needed for trees""",

    "neural network": """**Neural Networks** — deep learning fundamentals.

```python
# PyTorch — build and train a neural network
import torch
import torch.nn as nn
import torch.optim as optim

# Define model
class MLP(nn.Module):
    def __init__(self, input_size, hidden, output_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, output_size),
        )

    def forward(self, x):
        return self.net(x)

model = MLP(input_size=4, hidden=64, output_size=2)

# Loss & optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# Training loop
for epoch in range(100):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_t)
    loss    = criterion(outputs, y_train_t)
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        model.eval()
        with torch.no_grad():
            val_out = model(X_test_t)
            val_acc = (val_out.argmax(1) == y_test_t).float().mean()
        print(f"Epoch {epoch}: loss={loss:.4f} val_acc={val_acc:.3f}")
```

**Activation functions:**
- **ReLU** `max(0,x)` — most common hidden layer
- **Sigmoid** — binary output (0-1)
- **Softmax** — multi-class output (probabilities sum to 1)
- **GELU** — used in transformers (GPT, BERT)

**Optimizers:**
- **Adam** — best default choice
- **SGD + momentum** — often used in CV
- **AdamW** — Adam + weight decay (used in LLMs)""",

    # ── General ─────────────────────────────────────────────
    "data structures": """**Data Structures** — choose the right tool.

| Structure | Access | Search | Insert | Delete | Use when |
|-----------|--------|--------|--------|--------|----------|
| Array/List | O(1) | O(n) | O(n) | O(n) | index access |
| Dict/HashMap | O(1) | O(1) | O(1) | O(1) | key lookup |
| Set | — | O(1) | O(1) | O(1) | uniqueness, membership |
| Stack | O(1) top | O(n) | O(1) | O(1) | LIFO (undo, brackets) |
| Queue | O(1) | O(n) | O(1) | O(1) | FIFO (BFS, tasks) |
| Heap | O(1) min | O(n) | O(log n) | O(log n) | priority queue |
| Binary Tree | O(log n) | O(log n) | O(log n) | O(log n) | sorted data |

```python
# Stack (LIFO) — use list
stack = []
stack.append(1); stack.append(2)  # push
stack.pop()   # 2 (last in, first out)

# Queue (FIFO) — use deque
from collections import deque
q = deque()
q.append(1); q.append(2)     # enqueue
q.popleft()  # 1 (first in, first out)

# Priority Queue / Heap — use heapq
import heapq
heap = []
heapq.heappush(heap, 3)
heapq.heappush(heap, 1)
heapq.heappush(heap, 2)
heapq.heappop(heap)   # 1 (smallest first)

# For max-heap: negate values
heapq.heappush(heap, -10)
-heapq.heappop(heap)   # 10

# Counter
from collections import Counter
c = Counter("banana")   # {'a':3, 'n':2, 'b':1}
c.most_common(2)        # [('a',3), ('n',2)]

# OrderedDict (Python 3.7+ dicts already ordered)
from collections import OrderedDict
```""",

    "regex": r"""**Regular Expressions** — pattern matching.

```python
import re

text = "Contact: alice@example.com or bob@test.org, phone: 555-1234"

# Search — find first match
m = re.search(r'\d{3}-\d{4}', text)
m.group()   # '555-1234'

# Find all — list of matches
emails = re.findall(r'[\w.]+@[\w.]+\.\w+', text)
# ['alice@example.com', 'bob@test.org']

# Sub — replace
cleaned = re.sub(r'\s+', ' ', "hello   world")   # "hello world"

# Match (from start of string)
re.match(r'\d+', "123abc")     # matches
re.match(r'\d+', "abc123")     # doesn't match

# Compile for reuse (faster in loops)
pattern = re.compile(r'[\w.]+@[\w.]+\.\w+', re.IGNORECASE)
emails = pattern.findall(text)

# Groups
m = re.search(r'(\w+)@(\w+)\.(\w+)', text)
m.group(0)   # full: 'alice@example'
m.group(1)   # first: 'alice'
m.group(2)   # second: 'example'

# Named groups
m = re.search(r'(?P<user>\w+)@(?P<domain>\w+)', text)
m.group('user')    # 'alice'
m.group('domain')  # 'example'
```

**Common patterns:**
```
\d    digit           \D not digit
\w    word char       \W not word char
\s    whitespace      \S not whitespace
.     any char (not newline)
^     start of string
$     end of string
*     0 or more
+     1 or more
?     0 or 1
{n}   exactly n
{n,m} between n and m
[abc] character class
```""",

    "file handling": r"""**Python File Handling** — read, write, process files.

```python
# Read entire file
with open("data.txt") as f:
    content = f.read()       # single string

# Read lines
with open("data.txt") as f:
    lines = f.readlines()    # list of lines (with \n)
    lines = [l.strip() for l in f]  # strip whitespace

# Read line-by-line (memory-efficient for large files)
with open("large.txt") as f:
    for line in f:
        process(line.strip())

# Write
with open("out.txt", "w") as f:
    f.write("Hello, World!\n")
    f.writelines(["line1\n", "line2\n"])

# Append
with open("log.txt", "a") as f:
    f.write("new entry\n")

# JSON
import json

# Read JSON
with open("data.json") as f:
    data = json.load(f)

# Write JSON
with open("out.json", "w") as f:
    json.dump(data, f, indent=2)

# CSV
import csv

with open("data.csv") as f:
    reader = csv.DictReader(f)
    rows = list(reader)       # list of dicts

with open("out.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerows([{"name": "Alice", "age": 30}])

# Path operations (pathlib — preferred)
from pathlib import Path

p = Path("data/file.txt")
p.exists()           # True/False
p.read_text()        # read as string
p.write_text("hi")  # write string
p.parent             # data/
p.name               # file.txt
p.stem               # file
p.suffix             # .txt
list(Path(".").glob("*.py"))   # find Python files
```""",
}


# ─────────────────────────────────────────────────────────────
# INTENT DETECTION
# ─────────────────────────────────────────────────────────────

GREETING_WORDS = {"hi", "hello", "hey", "hlo", "hola", "yo", "sup", "howdy"}
SMALL_TALK_RE  = [r"\bhow are you\b", r"\bhow r u\b", r"\bwhat'?s up\b", r"\bu good\b"]
AFFIRMATION_WORDS = {"yes", "yup", "yep", "sure", "ok", "okay", "yeah", "correct", "right"}

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "python list":          ["list", "array", "append", "slice", "comprehension"],
    "python dict":          ["dict", "dictionary", "hashmap", "key", "value", "counter"],
    "python function":      ["function", "def", "lambda", "decorator", "args", "kwargs"],
    "python class":         ["class", "object", "oop", "inherit", "dataclass", "__init__"],
    "python async":         ["async", "await", "asyncio", "coroutine", "concurrent"],
    "python generator":     ["generator", "yield", "lazy", "iterator"],
    "binary search":        ["binary search", "bsearch", "bisect"],
    "sorting":              ["sort", "bubble sort", "merge sort", "quick sort", "timsort"],
    "recursion":            ["recursion", "recursive", "factorial", "fibonacci", "base case"],
    "dynamic programming":  ["dynamic programming", "dp", "memoization", "tabulation", "knapsack", "lcs", "coin change"],
    "big o":                ["big o", "complexity", "o(n)", "o(log n)", "time complexity", "space complexity"],
    "javascript promise":   ["promise", "async await", "then", "fetch", "axios"],
    "javascript closure":   ["closure", "scope", "private", "factory"],
    "javascript array":     ["map(", "filter(", "reduce(", "flatmap", "findindex"],
    "html":                 ["html", "tag", "form", "input", "element", "dom"],
    "css":                  ["css", "flexbox", "grid", "style", "animation", "responsive"],
    "rest api":             ["rest", "api", "endpoint", "crud", "get request", "post request", "http"],
    "sql":                  ["sql", "select", "join", "query", "database", "sqlite", "postgres"],
    "git":                  ["git", "commit", "branch", "merge", "push", "pull", "stash"],
    "docker":               ["docker", "container", "dockerfile", "compose", "image"],
    "machine learning":     ["machine learning", "ml", "classification", "regression", "sklearn", "random forest"],
    "neural network":       ["neural network", "deep learning", "pytorch", "tensorflow", "backprop", "layer"],
    "data structures":      ["stack", "queue", "heap", "linked list", "tree", "data structure"],
    "regex":                ["regex", "regular expression", "pattern", "re.findall", "re.sub"],
    "file handling":        ["file", "open(", "read file", "write file", "csv", "json load"],
}

GREETINGS = [
    "Hey! What are we building today?",
    "Hi there! Got a coding challenge?",
    "Hello! What can I help you solve?",
    "Hey — what problem are we tackling?",
    "Hi! Code question, concept, or something to debug?",
]

SMALL_TALK = [
    "Doing great, ready to help! What's the task?",
    "All good! Let's build something. What do you need?",
    "Fantastic! Got a coding challenge for me?",
]

CLARIFICATIONS = [
    "Can you give me a bit more detail? What language or framework?",
    "Tell me more — what's the specific problem or goal?",
    "What outcome are you looking for? Happy to help once I know more.",
]


def detect_intent(msg: str) -> str:
    m = msg.lower().strip()
    words = set(re.findall(r"\b\w+\b", m))

    if words & GREETING_WORDS and len(words) <= 4:
        return "greeting"
    if words & AFFIRMATION_WORDS and len(words) <= 3:
        return "affirmation"
    for pat in SMALL_TALK_RE:
        if re.search(pat, m):
            return "smalltalk"
    return "general"


def find_topic(msg: str) -> str | None:
    m = msg.lower()
    best_topic, best_score = None, 0
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in m)
        if score > best_score:
            best_score, best_topic = score, topic
    return best_topic if best_score > 0 else None


def smart_local_response(user_message: str, conversation_history: list = None) -> str:
    """
    Return a real, knowledgeable response — no API keys required.
    """
    intent = detect_intent(user_message)

    if intent == "greeting":
        return random.choice(GREETINGS)
    if intent == "smalltalk":
        return random.choice(SMALL_TALK)
    if intent == "affirmation":
        return random.choice([
            "Great! Tell me what you're working on.",
            "Cool! What specifically do you need?",
            "Sounds good — what's the first thing to tackle?",
        ])

    topic = find_topic(user_message)
    if topic and topic in KNOWLEDGE:
        return KNOWLEDGE[topic]

    msg_lower = user_message.lower()

    # Code execution hint
    if any(w in msg_lower for w in ["run", "execute", "output of"]):
        return (
            "To run code, type: **run: <your code here>** and I'll execute it locally and "
            "show the output.\n\nExample:\n```\nrun: print(sum(range(100)))\n```"
        )

    # Math questions
    if re.search(r"\d[\d\s\+\-\*\/\^\(\)]+\d", user_message):
        try:
            expr = re.findall(r"[\d\s\+\-\*\/\(\)\.]+", user_message)
            if expr:
                result = eval(expr[0].strip(), {"__builtins__": {}})
                return f"**Result:** `{expr[0].strip()} = {result}`"
        except Exception:
            pass

    return "local fallback"
