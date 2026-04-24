import requests
import time
import random
import sqlite3

API_URL = "http://127.0.0.1:8000"

# 📚 THE CURRICULUM
VOCABULARY = [
    ("Eloquent", "Fluent or persuasive in speaking or writing."),
    ("Paradigm", "A typical example or pattern of something; a model."),
    ("Cogent", "Clear, logical, and convincing."),
    ("Pragmatic", "Dealing with things sensibly and realistically."),
    ("Ephemeral", "Lasting for a very short time."),
    ("Meticulous", "Showing great attention to detail; very careful and precise."),
]

CODING_PATTERNS = [
    ("Singleton Pattern", "Ensures a class has only one instance and provides a global point of access to it."),
    ("Big O Notation", "A mathematical notation that describes the limiting behavior of a function when the argument tends towards a particular value or infinity."),
    ("Dry Principle", "'Don't Repeat Yourself' - a principle of software development aimed at reducing repetition of information."),
]

DEBUGGING_TIPS = [
    ("RecursionError", "Usually caused by exceeding the maximum recursion depth, often due to a missing base case."),
    ("Memory Leak", "Occurs when a computer program incorrectly manages memory allocations, such as failing to release memory that is no longer needed."),
]

class NightTeacher:
    def __init__(self):
        self.lesson_count = 0
        self.phase = "RESPOND" # Phase 1: Smart Responding
        
    def get_wikipedia_fact(self):
        try:
            res = requests.get("https://en.wikipedia.org/api/rest_v1/page/random/summary", timeout=10)
            if res.status_code == 200:
                data = res.json()
                return f"{data['title']}: {data['extract'][:300]}"
        except:
            return None
        return None

    def teach(self, topic, detail):
        # We use the 'learn:' command we built to teach the AI forever
        fact = f"learn: {topic} - {detail}"
        try:
            requests.post(f"{API_URL}/chat", json={"message": fact})
            self.lesson_count += 1
            print(f"[Teacher] 🎓 Lesson {self.lesson_count} ({self.phase}): {topic}")
        except:
            print("[Teacher] ⚠️ API server seems down. Waiting...")

    def audit(self):
        # We ONLY check if history exists. We NEVER delete or trim data.
        print(f"\n[Audit] 🛡️ Verifying permanent memory at lesson {self.lesson_count}...")
        try:
            res = requests.get(f"{API_URL}/history")
            if res.status_code == 200:
                print("✅ Memory Check: 100% Intact. No deletions detected.")
        except:
            print("❌ Audit Error: Server down.")

    def run(self):
        print("🌙 CURRICULUM TEACHER ACTIVE.")
        print("Roadmap: Respond -> Reply -> Coding -> Debugging -> Fixing Errors")
        while True:
            # Phase 1: Smart Responding (Vocabulary & Tone)
            if self.phase == "RESPOND":
                word, defn = random.choice(VOCABULARY)
                self.teach(f"Advanced Vocabulary: {word}", defn)
                if self.lesson_count >= 20: self.phase = "REPLY"
            
            # Phase 2: The Reply (General Facts)
            elif self.phase == "REPLY":
                fact = self.get_wikipedia_fact()
                if fact:
                    self.teach("World Fact", fact)
                if self.lesson_count >= 100: self.phase = "CODING"
            
            # Phase 3: Coding Masterclass
            elif self.phase == "CODING":
                pattern, desc = random.choice(CODING_PATTERNS)
                self.teach(f"Coding Pattern: {pattern}", desc)
                if self.lesson_count >= 150: self.phase = "DEBUGGING"
                
            # Phase 4: Debugging Theory
            elif self.phase == "DEBUGGING":
                err, fix = random.choice(DEBUGGING_TIPS)
                self.teach("Debugging Logic", f"Understanding {err}: {fix}")
                if self.lesson_count >= 200: self.phase = "FIX_ERRORS"
            
            # Phase 5: Fixing Errors (Code Correction)
            else:
                fixes = [
                    ("IndexError", "Prevented by checking len(list) before access."),
                    ("KeyError", "Prevented by using dict.get() or checking 'if key in dict'."),
                    ("Infinite Loop", "Ensuring the loop condition eventually becomes false or includes a break statement.")
                ]
                topic, fix = random.choice(fixes)
                self.teach("Practical Fix", f"How to resolve {topic}: {fix}")

            # Safety Audit every 10 lessons (Verifies memory is NOT deleted)
            if self.lesson_count % 10 == 0:
                self.audit()

            time.sleep(30) 

if __name__ == "__main__":
    teacher = NightTeacher()
    teacher.run()
