"""
teaching_curriculum.py
──────────────────────
Creates a teacher-like curriculum by adding detailed lessons to the knowledge base.
Covers fundamentals, step-by-step explanations, and best practices.

Run: python teaching_curriculum.py
"""

from db import add_or_update_knowledge, init_db, get_knowledge_context


LESSONS = [
    # ═══════════════════════════════════════════════════════════════
    # FUNDAMENTALS
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "variables_explained",
        "content": """
VARIABLES: Understanding the Basics
────────────────────────────────────
A variable is like a labeled box that stores data.

📦 CONCEPT: When you create a variable, you're naming a location in memory.

EXAMPLE (Python):
  name = "Alice"      # String variable
  age = 25            # Number variable
  is_student = True   # Boolean variable

WHY VARIABLES?
- Store data for later use
- Give data meaningful names
- Make code readable and maintainable

NAMING RULES:
✓ Use descriptive names: student_name (good)
✗ Avoid unclear names: x, temp (bad)
✓ Use snake_case for Python, camelCase for JavaScript
✓ Cannot start with numbers or special characters (except _)
"""
    },
    {
        "topic": "data_types_guide",
        "content": """
DATA TYPES: A Teacher's Guide
─────────────────────────────
Data types tell the computer what kind of data you're storing.

1️⃣ STRINGS (Text)
   Definition: Sequences of characters
   Examples: "hello", "Alice", "2024"
   Python: text = "Hello World"

2️⃣ NUMBERS
   Integers: Whole numbers (5, -3, 0)
   Floats: Decimal numbers (3.14, 2.5)
   Python: count = 5; price = 9.99

3️⃣ BOOLEANS (True/False)
   Definition: Values that are either True or False
   Used in conditions: if is_adult: ...

4️⃣ COLLECTIONS
   Lists: Ordered, changeable [1, 2, 3]
   Dictionaries: Key-value pairs {"name": "Bob"}
   Sets: Unique values {1, 2, 3}

KEY LESSON:
→ Choose the right type for your data
→ Different types have different methods
"""
    },
    {
        "topic": "functions_teaching",
        "content": """
FUNCTIONS: Learn Like A Teacher
───────────────────────────────
A function is a reusable block of code that performs a specific task.

🎯 ANATOMY OF A FUNCTION:
   def greet(name):           ← Function definition
       message = f"Hello {name}"  ← Body (what it does)
       return message         ← Return value

   result = greet("Alice")    ← Calling the function

📚 WHY USE FUNCTIONS?
1. Avoid repeating code (DRY = Don't Repeat Yourself)
2. Make code easier to test
3. Break complex problems into smaller pieces
4. Make code more readable

STEP-BY-STEP LEARNING:
Step 1: Write code that works for one case
Step 2: Identify repeated patterns
Step 3: Create a function to handle the pattern
Step 4: Test with different inputs

EXAMPLE - Converting Celsius to Fahrenheit:
def celsius_to_fahrenheit(celsius):
    fahrenheit = (celsius * 9/5) + 32
    return fahrenheit

# Test it
print(celsius_to_fahrenheit(0))    # Should be 32
print(celsius_to_fahrenheit(100))  # Should be 212
"""
    },
    {
        "topic": "loops_explained",
        "content": """
LOOPS: When to Use What
──────────────────────
Loops repeat code multiple times. There are two main types.

🔄 FOR LOOPS (When you know the count)
Definition: Repeat for each item in a collection
When to use: Processing every item in a list

Python Example:
  fruits = ["apple", "banana", "cherry"]
  for fruit in fruits:
      print(f"I like {fruit}")

JavaScript Example:
  for (let i = 0; i < 5; i++) {
      console.log(i);  // prints 0, 1, 2, 3, 4
  }

🔄 WHILE LOOPS (When you know the condition)
Definition: Repeat while a condition is true
When to use: Keep going until something happens

Python Example:
  count = 0
  while count < 5:
      print(count)
      count = count + 1

⚠️ LOOP SAFETY:
- Avoid infinite loops (loops that never stop)
- Always update the condition variable
- Test your loops with small data first

TEACHING TIP:
→ Use FOR loops for collections (lists, arrays)
→ Use WHILE loops for conditions (until user quits, etc.)
"""
    },
    # ═══════════════════════════════════════════════════════════════
    # OBJECT-ORIENTED PROGRAMMING
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "classes_oop",
        "content": """
CLASSES: Understanding Objects
───────────────────────────────
A class is a blueprint for creating objects.

🏗️ ANALOGY:
   Class = Cookie cutter template
   Object = Actual cookies made from the template

STRUCTURE:
class Car:
    def __init__(self, brand, color):  ← Constructor (setup)
        self.brand = brand             ← Attributes (properties)
        self.color = color

    def drive(self):                   ← Method (action)
        return f"{self.brand} is driving"

# Creating objects
my_car = Car("Toyota", "blue")
print(my_car.drive())  # Output: Toyota is driving

KEY CONCEPTS:
- Attributes: Data that objects have (brand, color, age)
- Methods: Actions that objects can do (drive, stop, honk)
- Encapsulation: Bundle data and actions together

TEACHING PROGRESSION:
1. Create a simple class with attributes
2. Add methods that use those attributes
3. Create multiple objects from the same class
4. Modify the class, see all objects update
"""
    },
    # ═══════════════════════════════════════════════════════════════
    # DATABASE FUNDAMENTALS
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "database_basics",
        "content": """
DATABASES: A Teacher's Introduction
────────────────────────────────────
A database is an organized collection of structured data.

📊 ANALOGY:
   Database = Library
   Table = Book shelf
   Row = Individual book
   Column = Book property (title, author, year)

SQLITE STRUCTURE:
CREATE TABLE students (
    id          INTEGER PRIMARY KEY,
    name        TEXT,
    age         INTEGER,
    grade       TEXT
);

KEY OPERATIONS (CRUD):
C = CREATE: INSERT INTO students (name, age, grade) VALUES ('Alice', 20, 'A')
R = READ:   SELECT * FROM students WHERE grade = 'A'
U = UPDATE: UPDATE students SET age = 21 WHERE name = 'Alice'
D = DELETE: DELETE FROM students WHERE id = 1

TEACHING PROGRESSION:
Step 1: Create a simple table
Step 2: Insert sample data
Step 3: Query data with SELECT
Step 4: Filter with WHERE
Step 5: Update and delete
Step 6: Join multiple tables
"""
    },
    # ═══════════════════════════════════════════════════════════════
    # WEB CONCEPTS
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "api_fundamentals",
        "content": """
APIs: What They Are and Why They Matter
────────────────────────────────────────
API = Application Programming Interface
It's how programs talk to each other.

🔌 REAL-WORLD ANALOGY:
   API = Restaurant menu
   You (Client) → Order from menu (API)
   Restaurant (Server) → Prepares food → Gives it to you
   You get food without knowing the kitchen details

HTTP METHODS (The "actions" in the menu):
1. GET:    Request data (read-only, safe)
2. POST:   Send data (create new)
3. PUT:    Replace data (update)
4. DELETE: Remove data

SIMPLE FASTAPI EXAMPLE:
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {"message": "Hello, World!"}

# Client requests: GET http://localhost:8000/hello
# Server responds: {"message": "Hello, World!"}

REQUEST → PROCESSING → RESPONSE CYCLE:
Client sends request with:
  - Method (GET, POST, etc.)
  - URL path (/users, /products)
  - Headers (metadata)
  - Body (optional data)

Server processes and returns:
  - Status code (200=OK, 404=Not Found, 500=Error)
  - Headers (metadata)
  - Response body (JSON, HTML, etc.)

TEACHING TIP:
→ Start with GET requests (simplest)
→ Move to POST (sending data)
→ Understand status codes
→ Practice with real APIs
"""
    },
    # ═══════════════════════════════════════════════════════════════
    # BEST PRACTICES
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "code_quality_guide",
        "content": """
CODE QUALITY: Write Like a Professional
────────────────────────────────────────

✓ READABLE CODE:
  Bad:  x=y+z
  Good: total_price = subtotal + tax

✓ MEANINGFUL NAMES:
  Bad:  def f(x): return x*2
  Good: def double_value(number): return number * 2

✓ SINGLE RESPONSIBILITY:
  One function = One job
  Bad:  def process_user_data(): # does too much
  Good: def validate_email(), def hash_password()

✓ DRY PRINCIPLE (Don't Repeat Yourself):
  If you write the same code 3+ times, make a function

✓ COMMENTS:
  Write comments for WHY, not WHAT
  Bad:  i = i + 1  # increment i
  Good: count = count + 1  # move to next valid entry

✓ ERROR HANDLING:
  try:
      user = fetch_user(id)
  except UserNotFoundError:
      print("User doesn't exist")

TESTING:
Before shipping code, test:
- Happy path (normal use)
- Edge cases (empty input, very large input)
- Error cases (what breaks it?)

CHECKLIST BEFORE SHARING CODE:
□ Does it work?
□ Is it readable?
□ Are there comments explaining WHY?
□ Did I test edge cases?
□ Can someone else understand it?
"""
    },
    {
        "topic": "debugging_methodology",
        "content": """
DEBUGGING: A Systematic Approach
─────────────────────────────────
Debugging is the process of finding and fixing bugs.

🐛 THE 5-STEP METHOD:

STEP 1: REPRODUCE THE BUG
  - Run the code that fails
  - Note exactly what goes wrong
  - Can you repeat it every time?

STEP 2: READ THE ERROR MESSAGE
  - Error messages tell you WHERE and sometimes WHY
  - Example: "IndexError: list index out of range"
  - This means you accessed a list element that doesn't exist

STEP 3: ADD PRINT STATEMENTS
  numbers = [1, 2, 3]
  print(f"List has {len(numbers)} items")
  print(numbers[5])  # This will crash

  Use print() to see what values actually are

STEP 4: USE BREAKPOINTS (Advanced)
  Stop execution at a specific line
  Inspect variable values
  Step through code line-by-line

STEP 5: ISOLATE THE PROBLEM
  - Comment out code sections
  - Test smaller pieces
  - When does it start failing?

COMMON BUGS:
• Off-by-one errors (using index 5 when list has 5 items)
• Null/None values (trying to use empty variables)
• Type mismatches (treating number as string)
• Infinite loops (condition never becomes false)

DEBUGGING MINDSET:
→ Stay calm, bugs are normal
→ Trust the error message
→ Use print() liberally
→ Test one change at a time
→ Read the code carefully (many bugs are typos)
"""
    },
    {
        "topic": "learning_path",
        "content": """
PROGRAMMING LEARNING PATH
──────────────────────────
A recommended order to learn programming concepts:

FOUNDATION (Week 1-2):
✓ Variables and data types
✓ Basic operations (+, -, *, /)
✓ Printing output
✓ Getting user input
Project: Simple calculator

CONTROL FLOW (Week 3):
✓ If/else statements
✓ Boolean logic (and, or, not)
✓ Comparison operators (==, <, >, <=, >=)
Project: Number guessing game

LOOPS (Week 4):
✓ For loops
✓ While loops
✓ Breaking out of loops
Project: Times table, pattern printing

FUNCTIONS (Week 5):
✓ Defining functions
✓ Parameters and return values
✓ Local vs global scope
Project: Calculator with functions

DATA STRUCTURES (Week 6):
✓ Lists (arrays)
✓ Dictionaries
✓ Sets
Project: To-do list, address book

INTERMEDIATE (Week 7-8):
✓ Classes and objects
✓ File I/O (reading/writing files)
✓ Error handling (try/except)
Project: Student management system

ADVANCED (Week 9+):
✓ APIs and web requests
✓ Databases
✓ Web frameworks
Project: Build a real application

LEARNING TIP:
→ Complete each stage before moving to next
→ Build projects, don't just read tutorials
→ Practice debugging your own code
→ Help others learn
"""
    },
]


def main():
    init_db()
    print("\n" + "=" * 60)
    print("🎓 LOADING TEACHER'S CURRICULUM INTO KNOWLEDGE BASE")
    print("=" * 60 + "\n")

    for lesson in LESSONS:
        add_or_update_knowledge(lesson["topic"], lesson["content"])
        print(f"✓ Loaded: {lesson['topic']}")

    print("\n" + "=" * 60)
    print("📚 CURRICULUM LOADED!")
    print("=" * 60)
    print("\nKnowledge Base Preview:\n")
    print(get_knowledge_context(max_entries=10))
    print("\n" + "=" * 60)
    print("The chatbot is now a TEACHER!")
    print("Try asking: 'Explain variables', 'What are loops?', etc.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
