"""
coding_teacher.py
─────────────────
Deterministic fallback replies for the local chatbot when a large coding
model is not available. The goal is to keep the assistant helpful, clear,
and code-oriented instead of returning low-quality generic generations.
"""

from __future__ import annotations

import re
import random


LANGUAGE_DEFINITIONS = [
    ("typescript", ["typescript", "ts"], "typescript"),
    ("javascript", ["javascript", "js", "node", "nodejs"], "javascript"),
    ("python", ["python", "py"], "python"),
    ("java", ["java"], "java"),
    ("c++", ["c++", "cpp"], "cpp"),
    ("c#", ["c#", "csharp"], "csharp"),
    ("go", ["golang", "go"], "go"),
    ("rust", ["rust"], "rust"),
    ("php", ["php"], "php"),
    ("ruby", ["ruby"], "ruby"),
    ("sql", ["sql", "sqlite"], "sql"),
    ("html", ["html"], "html"),
    ("css", ["css"], "css"),
    ("bash", ["bash", "shell", "sh"], "bash"),
    ("powershell", ["powershell", "pwsh"], "powershell"),
    ("c", [" c language ", " in c ", " c program "], "c"),
]

SUPPORTED_LANGUAGES = ", ".join(
    [
        "Python",
        "JavaScript",
        "TypeScript",
        "Java",
        "C",
        "C++",
        "C#",
        "Go",
        "Rust",
        "PHP",
        "SQL",
        "HTML/CSS",
        "Bash",
        "PowerShell",
    ]
)


def extract_latest_question(prompt: str) -> str:
    """Pulls the current user question out of the richer app prompt."""
    marker = "### Current Question:"
    if marker not in prompt:
        return prompt.strip()

    question = prompt.split(marker, maxsplit=1)[1]
    question = question.split("Please give a clear, helpful answer.", maxsplit=1)[0]
    return question.strip()


def detect_language(message: str) -> str | None:
    normalized = f" {re.sub(r'[^a-z0-9#+]+', ' ', message.lower())} "
    for canonical, aliases, _ in LANGUAGE_DEFINITIONS:
        for alias in aliases:
            if alias.startswith(" "):
                if alias in normalized:
                    return canonical
            elif any(char in alias for char in "#+"):
                if f" {alias} " in normalized:
                    return canonical
            elif re.search(rf"\b{re.escape(alias)}\b", normalized):
                return canonical
    return None


def code_fence(language: str) -> str:
    for canonical, _, fence in LANGUAGE_DEFINITIONS:
        if canonical == language:
            return fence
    return "text"


def wrap_code(language: str, code: str) -> str:
    return f"```{code_fence(language)}\n{code.strip()}\n```"


def explain_response(title: str, explanation: str, bullets: list[str] | None = None) -> str:
    lines = [f"**{title}**", explanation]
    if bullets:
        lines.extend(f"- {item}" for item in bullets)
    return "\n\n".join([lines[0], "\n".join(lines[1:])])


HELLO_WORLD = {
    "python": "print('Hello, World!')",
    "javascript": "console.log('Hello, World!');",
    "typescript": "console.log('Hello, World!');",
    "java": """public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}""",
    "c": """#include <stdio.h>

int main(void) {
    printf("Hello, World!\\n");
    return 0;
}""",
    "c++": """#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}""",
    "c#": """using System;

class Program {
    static void Main() {
        Console.WriteLine("Hello, World!");
    }
}""",
    "go": """package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}""",
    "rust": """fn main() {
    println!("Hello, World!");
}""",
    "php": """<?php
echo "Hello, World!";
""",
    "ruby": """puts "Hello, World!\"""",
    "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Hello</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>""",
    "bash": """echo "Hello, World!\"""",
    "powershell": """Write-Output "Hello, World!\"""",
}

ADD_TWO_NUMBERS = {
    "python": """def add(a, b):
    return a + b

print(add(2, 3))""",
    "javascript": """function add(a, b) {
  return a + b;
}

console.log(add(2, 3));""",
    "typescript": """function add(a: number, b: number): number {
  return a + b;
}

console.log(add(2, 3));""",
    "java": """public class Main {
    static int add(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        System.out.println(add(2, 3));
    }
}""",
    "c++": """#include <iostream>

int add(int a, int b) {
    return a + b;
}

int main() {
    std::cout << add(2, 3) << std::endl;
    return 0;
}""",
    "c#": """using System;

class Program {
    static int Add(int a, int b) {
        return a + b;
    }

    static void Main() {
        Console.WriteLine(Add(2, 3));
    }
}""",
    "go": """package main

import "fmt"

func add(a int, b int) int {
    return a + b
}

func main() {
    fmt.Println(add(2, 3))
}""",
    "rust": """fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    println!("{}", add(2, 3));
}""",
    "sql": """SELECT (2 + 3) AS sum_result;""",
}

READ_FILE = {
    "python": """with open("example.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)""",
    "javascript": """const fs = require("fs");
const content = fs.readFileSync("example.txt", "utf8");
console.log(content);""",
    "typescript": """import { readFileSync } from "fs";

const content = readFileSync("example.txt", "utf8");
console.log(content);""",
    "java": """import java.nio.file.Files;
import java.nio.file.Path;

public class Main {
    public static void main(String[] args) throws Exception {
        String content = Files.readString(Path.of("example.txt"));
        System.out.println(content);
    }
}""",
    "c#": """using System;
using System.IO;

class Program {
    static void Main() {
        string content = File.ReadAllText("example.txt");
        Console.WriteLine(content);
    }
}""",
    "go": """package main

import (
    "fmt"
    "os"
)

func main() {
    content, err := os.ReadFile("example.txt")
    if err != nil {
        panic(err)
    }

    fmt.Println(string(content))
}""",
    "rust": """use std::fs;

fn main() {
    let content = fs::read_to_string("example.txt").expect("failed to read file");
    println!("{}", content);
}""",
    "powershell": """$content = Get-Content -Path "example.txt" -Raw
Write-Output $content""",
    "bash": """cat example.txt""",
}

API_EXAMPLES = {
    "python": """from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI"}""",
    "javascript": """const express = require("express");

const app = express();

app.get("/hello", (req, res) => {
  res.json({ message: "Hello from Express" });
});

app.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});""",
    "typescript": """import express from "express";

const app = express();

app.get("/hello", (_req, res) => {
  res.json({ message: "Hello from Express" });
});

app.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});""",
    "go": """package main

import (
    "encoding/json"
    "net/http"
)

func hello(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{"message": "Hello from Go"})
}

func main() {
    http.HandleFunc("/hello", hello)
    http.ListenAndServe(":3000", nil)
}""",
}

SQLITE_EXAMPLES = {
    "python": """import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
conn.close()""",
    "javascript": """const Database = require("better-sqlite3");

const db = new Database("app.db");
const tables = db.prepare("SELECT name FROM sqlite_master WHERE type = ?").all("table");
console.log(tables);""",
    "typescript": """import Database from "better-sqlite3";

const db = new Database("app.db");
const tables = db.prepare("SELECT name FROM sqlite_master WHERE type = ?").all("table");
console.log(tables);""",
    "go": """package main

import (
    "database/sql"
    "fmt"
    _ "modernc.org/sqlite"
)

func main() {
    db, err := sql.Open("sqlite", "app.db")
    if err != nil {
        panic(err)
    }
    defer db.Close()

    rows, err := db.Query("SELECT name FROM sqlite_master WHERE type = 'table'")
    if err != nil {
        panic(err)
    }
    defer rows.Close()

    for rows.Next() {
        var name string
        rows.Scan(&name)
        fmt.Println(name)
    }
}""",
    "sql": """SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;""",
}

CONCEPT_EXPLANATIONS = {
    "api": (
        "API",
        "An API is a way for one program to talk to another using a defined set of inputs and outputs.",
        [
            "A client sends a request.",
            "A server processes it and sends back a response.",
            "In web APIs, this is usually done with HTTP methods like GET, POST, PUT, and DELETE.",
        ],
    ),
    "function": (
        "Function",
        "A function is a reusable block of code that takes input, does some work, and can return output.",
        [
            "Functions reduce repetition.",
            "They make code easier to test.",
            "They help you separate one task from another.",
        ],
    ),
    "loop": (
        "Loop",
        "A loop repeats a block of code until a condition is no longer true or until it finishes iterating over a collection.",
        [
            "Use a `for` loop when you know what you are iterating over.",
            "Use a `while` loop when repetition depends on a condition.",
        ],
    ),
    "class": (
        "Class",
        "A class is a blueprint for creating objects that bundle data and behavior together.",
        [
            "Fields store state.",
            "Methods define behavior.",
            "Classes are common in object-oriented programming.",
        ],
    ),
    "sql": (
        "SQL",
        "SQL is the language used to query and modify relational databases.",
        [
            "Use `SELECT` to read data.",
            "Use `INSERT`, `UPDATE`, and `DELETE` to change data.",
            "Use `WHERE` to filter rows.",
        ],
    ),
}


CODE_INTROS = [
    "Here you go:",
    "Try this:",
    "Here's one way:",
    "Sure:",
    "Like this:",
    "This should work:",
]

HOW_IT_WORKS_INTROS = [
    "How it works:",
    "Quick breakdown:",
    "What it does:",
    "In short:",
]


def build_code_answer(language: str, title: str, code: str, notes: list[str]) -> str:
    intro = random.choice(CODE_INTROS)
    breakdown = random.choice(HOW_IT_WORKS_INTROS)
    return (
        f"{intro}\n\n"
        f"{wrap_code(language, code)}\n\n"
        f"{breakdown}\n"
        + "\n".join(f"- {note}" for note in notes)
    )


# ═══════════════════════════════════════════════════════════════
# VARIED RESPONSES — picks random reply so bot doesn't repeat
# ═══════════════════════════════════════════════════════════════

GREETINGS = [
    "Hey! So good to see you. How's your day going?",
    "Hi there! I'm here and ready to chat or code—whatever you need!",
    "Hello! It's always great talking to you. What's on your mind today?",
    "Hey! Got anything fun you want to build or talk about?",
    "Hi friend! I'm doing great, thanks for asking. How can I help you today?",
    "Hey there! Ready to write some code, or do you just want to hang out and chat?",
]

THANKS_REPLIES = [
    "You're very welcome. Let me know if you need further optimization.",
    "My pleasure. Quality architecture is what I'm here for.",
    "Always happy to help you build reliable software.",
    "No problem at all. Let's keep coding!",
    "Glad that resolved it. I'll be here if you hit another roadblock.",
]

BYE_REPLIES = [
    "Farewell! Keep writing excellent code.",
    "Goodbye! I'll be here whenever you need high-speed debugging.",
    "Take care. Deploy with confidence!",
    "Until next time. Shutting down local session context.",
]

HOW_ARE_YOU = [
    "I'm doing fantastic, just hanging out here waiting for you! How are you?",
    "I'm feeling great! Excited to see what we'll do today. What's up?",
    "Couldn't be better. Always happy to chat with you! What's on your mind?",
]

CONFUSED = [
    "I want to give you the most accurate technical answer. Could you elaborate on the specifics?",
    "That is quite brief. What specific language, framework, or outcome are you targeting?",
    "Could you provide a bit more context? The more details regarding your system, the better my code will be.",
    "I'm analyzing your request, but I need more parameters to generate the correct architecture.",
]

AFFIRMATIVES = ["yes", "yeah", "yep", "sure", "ok", "okay", "y"]
NEGATIVES = ["no", "nope", "n", "not really"]

AFFIRMATIVE_REPLIES = [
    "Understood. Proceeding with your parameters. What's the next step?",
    "Acknowledged. I've updated my context. How shall we expand on this?",
    "Excellent. This aligns with standard practices. What else do you need?",
]

NEGATIVE_REPLIES = [
    "Understood. We will discard that approach. Let me know what you'd like to do instead.",
    "No problem. I will eagerly await your next directive.",
    "Alright, pivoting away from that. What is our new objective?",
]


def wants_detailed_explanation(lower: str) -> bool:
    """Detect if user actually wants a long, detailed answer."""
    detail_triggers = [
        "explain", "teach", "how does", "tell me about",
        "in detail", "deeply", "full", "everything about",
        "step by step", "walk me through",
    ]
    return any(trigger in lower for trigger in detail_triggers)


def wants_code(lower: str) -> bool:
    """Detect if user wants code."""
    code_triggers = ["write", "show", "code", "example",
                     "program", "function", "script", "create", "make"]
    return any(trigger in lower for trigger in code_triggers)


SHORT_CODE_PREFIXES = [
    "Here:\n\n",
    "Try this:\n\n",
    "Sure:\n\n",
    "Got it:\n\n",
    "Here you go:\n\n",
    "Easy:\n\n",
]


def short_code_answer(language: str, code: str) -> str:
    """Short code reply with a varied one-word lead-in."""
    prefix = random.choice(SHORT_CODE_PREFIXES)
    return f"{prefix}{wrap_code(language, code)}"


SHORT_CONCEPT_TEMPLATES = [
    "**{title}**: {explanation}",
    "{title} — {explanation}",
    "{explanation}",
    "In short: {explanation}",
    "{title}: {explanation}",
]


def short_concept(title: str, explanation: str) -> str:
    return random.choice(SHORT_CONCEPT_TEMPLATES).format(
        title=title, explanation=explanation
    )


def generate_rule_based_response(message: str) -> str:
    user_message = message.strip()
    lower = user_message.lower().rstrip("!.?")
    language = detect_language(user_message) or "python"
    detailed = wants_detailed_explanation(lower)

    # Empty message
    if not user_message:
        return "Hi! What do you need?"

    # Greetings — short varied replies
    if lower in {"hello", "hi", "hey", "yo", "hai", "helo", "hlo"}:
        return random.choice(GREETINGS)

    # How are you
    if any(p in lower for p in ["how are you", "how r u", "how are u", "whats up", "what's up", "sup"]):
        return random.choice(HOW_ARE_YOU)

    # Thanks
    if any(p in lower for p in ["thank", "thanks", "thx", "ty"]):
        return random.choice(THANKS_REPLIES)

    # Goodbye
    if lower in {"bye", "goodbye", "see you", "cya", "later"}:
        return random.choice(BYE_REPLIES)

    # Yes/No
    if lower in AFFIRMATIVES:
        return random.choice(AFFIRMATIVE_REPLIES)
    if lower in NEGATIVES:
        return random.choice(NEGATIVE_REPLIES)

    # Very short messages with no clear intent
    if len(user_message.split()) <= 2 and not wants_code(lower):
        return random.choice(CONFUSED)

    # Concept explanations — short unless user says "explain"
    for concept, (title, explanation, bullets) in CONCEPT_EXPLANATIONS.items():
        if (
            re.search(rf"\b(what is|explain|define)\s+(an?\s+)?{re.escape(concept)}\b", lower)
            or re.search(rf"\bwhat\s+(an?\s+)?{re.escape(concept)}\s+is\b", lower)
        ):
            if detailed:
                return explain_response(title, explanation, bullets)
            return short_concept(title, explanation)

    # Hello world
    if "hello world" in lower:
        code = HELLO_WORLD.get(language, HELLO_WORLD["python"])
        if detailed:
            return build_code_answer(language, "hello world", code,
                ["Prints a greeting.", "Good to test your setup."])
        return short_code_answer(language, code)

    # Add numbers
    if "add two numbers" in lower or "sum two numbers" in lower or "add numbers" in lower:
        code = ADD_TWO_NUMBERS.get(language, ADD_TWO_NUMBERS["python"])
        if detailed:
            return build_code_answer(language, "adding two numbers", code,
                ["Takes two inputs.", "Returns their sum."])
        return short_code_answer(language, code)

    # List tables
    if "list all tables" in lower or "list tables" in lower:
        return short_code_answer("sql", SQLITE_EXAMPLES["sql"])

    # Read file
    if "read file" in lower or "read a file" in lower:
        code = READ_FILE.get(language, READ_FILE["python"])
        return short_code_answer(language, code)

    # SQLite / DB
    if "sqlite" in lower or ("database" in lower and ("connect" in lower or "query" in lower)):
        code = SQLITE_EXAMPLES.get(language, SQLITE_EXAMPLES["python"])
        return short_code_answer(language, code)

    # APIs
    if "api" in lower or "endpoint" in lower:
        code = API_EXAMPLES.get(language, API_EXAMPLES["python"])
        if detailed:
            return build_code_answer(language, "API endpoint", code,
                ["One route.", "Returns JSON."])
        return short_code_answer(language, code)

    # Debugging — short prompt
    if "error" in lower or "debug" in lower or "fix" in lower or "bug" in lower:
        return random.choice([
            "Share the error message and the code.",
            "Paste the error + code — I'll help fix it.",
            "What's the error? Show me the code.",
        ])

    # Generic code request with no specifics
    if wants_code(lower):
        return random.choice([
            f"I am ready to write the {language.title()} implementation. Could you specify the exact functionality you need?",
            f"Certainly. To output accurate {language.title()} code, I just need to know the specific algorithmic or structural goal.",
            f"I can generate production-ready {language.title()} for this. What are the exact requirements?",
        ])

    # Fallback — short and asking
    return random.choice([
        "That's super interesting! Tell me more about it.",
        "Oh really? I'd love to hear your thoughts on that.",
        "Haha, absolutely! So, what should we work on next?",
        "I totally get what you mean! If you ever want to write some code related to that, just let me know.",
        "That makes total sense! How can I help you out right now?",
    ])
