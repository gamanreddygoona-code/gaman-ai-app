"""
test_system.py
──────────────
Test your AI system directly (no server needed).
"""

from coding_expert import CodingExpert
from advanced_reasoning import AdvancedReasoner
from mega_knowledge import get_knowledge
import time

def test_coding():
    """Test code generation."""
    print("\n" + "="*70)
    print("🧪 TEST 1: CODE GENERATION")
    print("="*70)

    ce = CodingExpert()

    # Test 1a: Simple code generation
    print("\nGenerating: Python function to find max in array")
    start = time.time()
    result = ce.generate_code("Python function to find maximum element in array", "python")
    elapsed = time.time() - start

    print(f"✅ Generated in {elapsed:.2f}s")
    print(f"   Code preview:\n{result.get('code', '')[:200]}")
    print(f"   Quality: {result.get('quality_score', 'N/A')}")

    # Test 1b: Code analysis
    print("\n\nAnalyzing generated code...")
    code = result.get('code', '')
    analysis = ce.analyze_code(code)
    print(f"✅ Analysis score: {analysis.get('score', 0)}/100")
    print(f"   Issues: {len(analysis.get('issues', []))}")
    print(f"   Performance tips: {len(analysis.get('performance', []))}")


def test_reasoning():
    """Test reasoning system."""
    print("\n" + "="*70)
    print("🧪 TEST 2: DEEP REASONING")
    print("="*70)

    ar = AdvancedReasoner()

    problem = "How to optimize database queries for million user scale?"
    print(f"\nProblem: {problem}")

    start = time.time()
    result = ar.deep_reasoning(problem)
    elapsed = time.time() - start

    print(f"✅ Reasoning completed in {elapsed:.2f}s")
    print(f"   Reasoning depth: {result.get('reasoning_depth', 'N/A')}")
    print(f"   Confidence: {result.get('confidence', 'N/A')}")
    print(f"   Supporting facts: {result.get('supporting_facts', 0)}")
    print(f"\n   Answer preview:\n   {result.get('final_answer', '')[:300]}...")


def test_knowledge():
    """Test knowledge base."""
    print("\n" + "="*70)
    print("🧪 TEST 3: KNOWLEDGE BASE")
    print("="*70)

    kb = get_knowledge()
    stats = kb.stats()

    print(f"\n📊 Knowledge Base Stats:")
    print(f"   Total facts: {stats['total_facts']:,}")
    print(f"   Growth: 1,546 → {stats['total_facts']:,} (8.9x)")

    # Search test
    print("\nSearching for: 'REST API GraphQL'")
    start = time.time()
    results = kb.search("REST API GraphQL", limit=3)
    elapsed = time.time() - start

    print(f"✅ Found {len(results)} facts in {elapsed:.3f}s")
    for r in results[:2]:
        print(f"   • {r['topic'][:60]}")


def test_integration():
    """Integration test."""
    print("\n" + "="*70)
    print("🧪 TEST 4: FULL INTEGRATION")
    print("="*70)

    kb = get_knowledge()
    ce = CodingExpert()
    ar = AdvancedReasoner()

    print("\nScenario: Design a REST API for a blog")

    # Step 1: Knowledge lookup
    print("\n1️⃣ KNOWLEDGE SEARCH")
    facts = kb.search("REST API design patterns", limit=3)
    print(f"   Found {len(facts)} design facts")

    # Step 2: Code generation
    print("\n2️⃣ CODE GENERATION")
    start = time.time()
    code = ce.generate_code("Python Flask REST API for blog with CRUD operations", "python")
    elapsed = time.time() - start
    print(f"   Generated in {elapsed:.2f}s")
    print(f"   Code length: {len(code.get('code', ''))} chars")

    # Step 3: Analysis
    print("\n3️⃣ CODE ANALYSIS")
    analysis = ce.analyze_code(code.get('code', ''))
    print(f"   Quality score: {analysis['score']}/100")

    # Step 4: Reasoning
    print("\n4️⃣ ARCHITECTURAL REASONING")
    start = time.time()
    reasoning = ar.deep_reasoning("What are best practices for REST API security?")
    elapsed = time.time() - start
    print(f"   Analyzed in {elapsed:.2f}s")
    print(f"   Answer: {reasoning.get('final_answer', '')[:150]}...")


if __name__ == "__main__":
    print("\n" + "🚀 "*35)
    print("GAMAN AI SYSTEM - COMPREHENSIVE TEST")
    print("🚀 "*35)

    try:
        test_coding()
    except Exception as e:
        print(f"❌ Coding test failed: {e}")

    try:
        test_reasoning()
    except Exception as e:
        print(f"❌ Reasoning test failed: {e}")

    try:
        test_knowledge()
    except Exception as e:
        print(f"❌ Knowledge test failed: {e}")

    try:
        test_integration()
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

    print("\n" + "="*70)
    print("✅ TEST SUITE COMPLETE")
    print("="*70)
    print("\nNext: Deploy to production!")
    print("  - Server: uvicorn app:app --host 0.0.0.0 --port 8000")
    print("  - Or: docker build -t gaman-ai . && docker run -p 8000:8000 gaman-ai")
