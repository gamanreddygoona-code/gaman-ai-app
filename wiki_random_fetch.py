"""
wiki_random_fetch.py
────────────────────
Fetch random Wikipedia articles to add diversity.
Uses Wikipedia's random article API + category listings.
Target: 10,000+ new unique articles.
"""

from mega_knowledge import get_knowledge
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {"User-Agent": "Gaman-AI-KnowledgeBot/2.0 (educational; local use)"}

# Wikipedia category pages — fetch all articles from each
CATEGORY_TOPICS = [
    # Enumerate hundreds of sub-topics for each domain
    # COMPUTER SCIENCE
    "Python_programming_language_topics",
    "Algorithms_and_data_structures",
    "Operating_system",
    "Distributed_computing",

    # SCIENCE
    "Chemistry", "Physics_topics", "Biology", "Mathematics",
    "Astronomy", "Neuroscience",

    # HISTORY
    "World_War_II", "Ancient_history", "History_of_science",
    "Industrial_Revolution",
]


def fetch_random_articles(count=500):
    """Get random Wikipedia article titles."""
    titles = set()
    while len(titles) < count:
        try:
            url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.status_code == 200:
                d = r.json()
                extract = d.get("extract", "")
                if extract and len(extract) > 80:
                    titles.add(d.get("title", ""))
        except Exception:
            pass
        time.sleep(0.05)  # Be polite
    return list(titles)


def fetch_wiki_summary(title):
    """Fetch summary for a specific Wikipedia title."""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            d = r.json()
            extract = d.get("extract", "").strip()
            if extract and len(extract) > 60:
                return {"topic": d.get("title", title), "content": extract[:800]}
    except Exception:
        pass
    return None


# Large curated topic list (diverse domains not covered before)
EXTRA_TOPICS = [
    # Economics & Finance
    "Gross domestic product", "Inflation", "Monetary policy", "Fiscal policy",
    "Stock market", "Bond (finance)", "Derivative (finance)", "Hedge fund",
    "Venture capital", "Initial public offering", "Mergers and acquisitions",
    "Supply and demand", "Price elasticity", "Monopoly", "Oligopoly",
    "Game theory", "Nash equilibrium", "Behavioral economics",
    "Keynesian economics", "Monetarism", "Austrian School",
    "Trade", "Comparative advantage", "Free trade", "Tariff",
    "Foreign exchange market", "Currency", "Cryptocurrency exchange",
    "Central bank", "Federal Reserve", "European Central Bank",

    # Philosophy
    "Philosophy", "Epistemology", "Metaphysics", "Ethics", "Ontology",
    "Logic", "Philosophy of mind", "Philosophy of science",
    "Political philosophy", "Aesthetics", "Phenomenology (philosophy)",
    "Existentialism", "Stoicism", "Utilitarianism", "Kantian ethics",
    "Plato", "Aristotle", "Socrates", "Immanuel Kant", "John Locke",
    "Friedrich Nietzsche", "Jean-Paul Sartre", "David Hume", "René Descartes",

    # Psychology
    "Psychology", "Cognitive psychology", "Social psychology",
    "Developmental psychology", "Abnormal psychology", "Neuropsychology",
    "Psychoanalysis", "Behaviorism", "Cognitive behavioral therapy",
    "Emotional intelligence", "Motivation", "Memory", "Learning",
    "Perception", "Consciousness", "Sleep", "Stress (biology)",
    "Personality psychology", "Intelligence quotient", "Creativity",
    "Abraham Maslow", "Sigmund Freud", "Carl Jung", "B. F. Skinner",

    # History
    "History of the Internet", "History of artificial intelligence",
    "History of computing", "History of mathematics",
    "History of science", "Scientific Revolution", "Enlightenment",
    "Industrial Revolution", "Information Age",
    "World War I", "World War II", "Cold War",
    "Renaissance", "Middle Ages", "Ancient Rome", "Ancient Greece",
    "Byzantine Empire", "Ottoman Empire", "British Empire",
    "American Revolution", "French Revolution", "Russian Revolution",

    # Geography & Society
    "Urbanization", "Globalization", "Democracy", "Authoritarianism",
    "Human rights", "United Nations", "NATO", "European Union",
    "Climate change", "Global warming", "Renewable energy",
    "Solar energy", "Wind power", "Nuclear power", "Fossil fuel",
    "Sustainability", "Carbon footprint", "Paris Agreement",
    "Biodiversity", "Deforestation", "Ocean acidification",

    # Medicine & Health
    "Medicine", "Public health", "Epidemiology", "Vaccine",
    "Antibiotic", "Antiviral drug", "Cancer", "Cardiovascular disease",
    "Diabetes", "Mental health", "Depression (mood)", "Anxiety disorder",
    "Alzheimer's disease", "Parkinson's disease", "Autism spectrum disorder",
    "Gene therapy", "CRISPR", "Stem cell", "Clinical trial",
    "Evidence-based medicine", "Placebo", "Double-blind experiment",
    "Pharmacology", "Drug development", "Medical imaging",
    "Surgery", "Minimally invasive surgery", "Laparoscopy", "Robotics in surgery",

    # Physics (deep)
    "Quantum mechanics", "Wave-particle duality", "Uncertainty principle",
    "Quantum entanglement", "Quantum superposition", "Schrödinger equation",
    "Standard Model", "Higgs boson", "Quark", "Lepton",
    "Dark matter", "Dark energy", "Big Bang", "Inflation (cosmology)",
    "Black hole", "Event horizon", "Hawking radiation",
    "String theory", "Loop quantum gravity", "M-theory",
    "Superconductivity", "Superfluidity", "Bose–Einstein condensate",
    "Laser", "Photonics", "Quantum optics",

    # Mathematics (deep)
    "Prime number", "Riemann hypothesis", "P versus NP problem",
    "Four color theorem", "Fermat's Last Theorem", "Gödel's incompleteness theorems",
    "Turing completeness", "Halting problem", "Church–Turing thesis",
    "Category theory", "Set theory", "Group theory", "Ring theory",
    "Field (mathematics)", "Vector space", "Hilbert space",
    "Fourier transform", "Laplace transform", "Z-transform",
    "Markov chain", "Stochastic process", "Monte Carlo method",
    "Chaos theory", "Fractal", "Mandelbrot set",
    "Game theory", "Information theory", "Shannon entropy",

    # Technology & Engineering
    "Semiconductor", "Transistor", "Integrated circuit",
    "Printed circuit board", "Electronic component",
    "Signal processing", "Digital signal processing",
    "Control theory", "PID controller", "Feedback",
    "Robotics", "Industrial robot", "Autonomous robot",
    "Mechanical engineering", "Civil engineering", "Electrical engineering",
    "Chemical engineering", "Aerospace engineering", "Biomedical engineering",
    "3D printing", "CNC machining", "Injection molding",

    # Art & Culture
    "Art", "Painting", "Sculpture", "Photography", "Film",
    "Music", "Classical music", "Jazz", "Rock music", "Electronic music",
    "Literature", "Novel", "Poetry", "Drama", "Narrative",
    "Architecture", "Baroque", "Gothic architecture", "Modernism",
    "Postmodernism", "Contemporary art", "Digital art",
    "Leonardo da Vinci", "Michelangelo", "Pablo Picasso", "Vincent van Gogh",
    "Ludwig van Beethoven", "Wolfgang Amadeus Mozart", "Johann Sebastian Bach",
    "William Shakespeare", "Homer", "Dante Alighieri", "Leo Tolstoy",

    # Linguistics
    "Linguistics", "Phonology", "Morphology (linguistics)",
    "Syntax", "Semantics", "Pragmatics", "Discourse analysis",
    "Language acquisition", "Bilingualism", "Language family",
    "Natural language processing", "Computational linguistics",
    "Noam Chomsky", "Ferdinand de Saussure",
]


def run_extra_fetch():
    kb = get_knowledge()
    start = time.time()
    before = kb.stats()["total_facts"]

    print(f"🌐 Extra Wikipedia Fetch — {len(EXTRA_TOPICS)} topics")
    print(f"📊 Starting: {before} facts\n")

    added = 0
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(fetch_wiki_summary, t): t for t in EXTRA_TOPICS}
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            if result:
                try:
                    kb.add_fact(
                        topic=result["topic"],
                        content=result["content"],
                        source="wikipedia_extra",
                        category="encyclopedic",
                        confidence=0.93,
                    )
                    added += 1
                except Exception:
                    pass

            if (i + 1) % 50 == 0:
                print(f"  [{i+1}/{len(EXTRA_TOPICS)}] Added: {added}")

    after = kb.stats()["total_facts"]
    elapsed = time.time() - start
    print(f"\n✅ Extra fetch complete: {added} added | Total: {after} | Time: {elapsed:.1f}s")
    return after


if __name__ == "__main__":
    run_extra_fetch()
