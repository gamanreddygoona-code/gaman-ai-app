import os
from pymongo import MongoClient
from datetime import datetime

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "gaman_ai")

client = None
db = None

if MONGODB_URI:
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]

def is_mongodb_enabled():
    return db is not None

def init_mongodb():
    if not is_mongodb_enabled():
        return
    
    # Create collections if they don't exist
    if "chat_history" not in db.list_collection_names():
        db.create_collection("chat_history")
    
    if "knowledge" not in db.list_collection_names():
        db.create_collection("knowledge")
        starter_knowledge = [
            {"topic": "identity", "content": "You are a helpful coding assistant powered by a fine-tuned CodeLlama model.", "added_at": datetime.utcnow()},
            {"topic": "style", "content": "Always reply with clean, well-commented code. Prefer Python unless another language is asked for.", "added_at": datetime.utcnow()},
            {"topic": "database", "content": "The application uses MongoDB for chat history and knowledge storage.", "added_at": datetime.utcnow()},
        ]
        db.knowledge.insert_many(starter_knowledge)
    
    print("[mongodb] ✅ MongoDB initialised.")

def save_chat_mongo(user_message, bot_response):
    if not is_mongodb_enabled():
        return
    db.chat_history.insert_one({
        "user_message": user_message,
        "bot_response": bot_response,
        "created_at": datetime.utcnow()
    })

def get_chat_history_mongo(limit=20):
    if not is_mongodb_enabled():
        return []
    cursor = db.chat_history.find().sort("created_at", -1).limit(limit)
    history = []
    for doc in cursor:
        history.append({"user": doc["user_message"], "bot": doc["bot_response"]})
    return history[::-1]

def get_knowledge_context_mongo(max_entries=5):
    if not is_mongodb_enabled():
        return ""
    cursor = db.knowledge.find().sort("added_at", -1).limit(max_entries)
    lines = ["### System Knowledge:"]
    for doc in cursor:
        lines.append(f"- [{doc['topic']}] {doc['content']}")
    return "\n".join(lines)

def add_knowledge_mongo(topic, content):
    if not is_mongodb_enabled():
        return
    db.knowledge.update_one(
        {"topic": topic},
        {"$set": {"content": content, "added_at": datetime.utcnow()}},
        upsert=True
    )
