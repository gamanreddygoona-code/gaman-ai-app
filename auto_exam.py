import requests
import time

API_URL = "http://127.0.0.1:8000"

EXAM_QUESTIONS = [
    {
        "q": "What is the capital of France?",
        "a": "The capital of France is Paris. It is known for the Eiffel Tower and its rich history in art and culture."
    },
    {
        "q": "How does photosynthesis work?",
        "a": "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water. It generates oxygen as a byproduct."
    },
    {
        "q": "What is the time complexity of a binary search?",
        "a": "The time complexity of a binary search is O(log n), because it halves the search space during each step."
    },
    {
        "q": "Who wrote Romeo and Juliet?",
        "a": "Romeo and Juliet was written by William Shakespeare early in his career."
    },
    {
        "q": "Can you explain what an API is in simple terms?",
        "a": "An API (Application Programming Interface) is like a waiter in a restaurant. You tell the waiter what you want, the waiter tells the kitchen (the server), and then brings your food (the data) back to you."
    }
]

print("🎓 Starting AI Automated Exam & Teaching Sequence...")
print("=" * 60)

for idx, item in enumerate(EXAM_QUESTIONS):
    question = item["q"]
    correct_answer = item["a"]
    
    print(f"\n[Question {idx+1}/{len(EXAM_QUESTIONS)}]: {question}")
    
    try:
        # Ask the bot
        res = requests.post(f"{API_URL}/chat", json={"message": question})
        if res.status_code != 200:
            print("⚠️ Server error on /chat.")
            continue
            
        data = res.json()
        bot_reply = data.get("reply", "")
        source = data.get("source", "unknown")
        
        print(f"🤖 Bot ({source}): {bot_reply[:80]}...")
        
        # If the bot falls back to 'local', it means it didn't know the answer.
        if source == "local":
            print(f"❌ Bot failed to find a smart answer (used fallback).")
            print(f"📚 Teaching the bot the correct answer...")
            
            # 1. Teach it via /knowledge (Optional, for context injection if built that way)
            requests.post(f"{API_URL}/knowledge", json={
                "topic": question,
                "content": correct_answer
            })
            
            # 2. Teach it via /feedback with 5 stars so the learning_system stores it!
            fb_res = requests.post(f"{API_URL}/feedback", json={
                "user_message": question,
                "bot_response": correct_answer,
                "rating": 5,
                "feedback_text": "Perfect answer injected by automated examiner."
            })
            
            if fb_res.status_code == 200:
                print("✅ Successfully taught the bot!")
                
                # Check learning: Ask again!
                print("🔍 Re-testing the bot to ensure it learned...")
                time.sleep(1) # simulate brief pause
                test_res = requests.post(f"{API_URL}/chat", json={"message": question})
                test_data = test_res.json()
                
                if test_data.get("source") in ["learned", "trained"]:
                    print(f"🎉 Bot successfully learned! New response ({test_data['source']}): {test_data['reply'][:50]}...")
                else:
                    print(f"⚠️ Bot still answered using {test_data.get('source')}.")
            else:
                print("⚠️ Failed to submit feedback training.")
        else:
            print(f"✅ Bot answered smartly using {source}! No teaching required.")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the server running on port 8000?")
        break
        
print("\n" + "=" * 60)
print("🏁 Examination Complete. Bot intelligence increased.")
