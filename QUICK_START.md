# 🚀 QUICK START - Real Gaman AI

## Start the Chatbot

```bash
cd C:\Gamansai\ai
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Then open: **http://127.0.0.1:8000**

---

## Try These Commands

### 1. Ask a Coding Question
```
User: "write a python hello world"
Bot:  🤖 trained  →  Uses your trained database
      "Sure: ```python\nprint('Hello, World!')\n```"
```

### 2. Generate a Real Game
```
User: "create a shooter game"
Bot:  🎮 Real Shooter Game Generated!
      [Click link to play immediately]
```

### 3. Generate a Real 3D Model
```
User: "make a dragon 3D model"
Bot:  ✅ Real 3D model generated!
      🎨 244 vertices, 472 faces
      📥 Download .glb file
```

### 4. Rate a Response
```
Click ⭐⭐⭐⭐⭐ stars to train the bot
Bot learns and reuses high-rated answers
```

---

## Enable Claude API (Optional)

For real AI responses:

```bash
# 1. Get free API key at: https://console.anthropic.com
# 2. Set environment variable:
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Restart server
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Now responses will use Claude AI (source: ✨ claude)

---

## What's Real vs What's Optional

### ✅ ALWAYS WORKING (No setup needed)
- Real trained database model (81 patterns)
- Real playable games (Collector, Shooter, Platformer)
- Real 3D models (.glb files)
- Feedback learning (5-star ratings)
- Code templates (Python, JS, Java, etc)
- Knowledge base (28 topics)

### ⚠️  OPTIONAL (Needs setup)
- Claude API (needs ANTHROPIC_API_KEY)

### 🛠️ FALLBACK
- Rule-based responses (greetings, patterns)

---

## Retrain the Model

If you add more conversations:

```bash
cd C:\Gamansai\ai
python train_from_database.py
```

This will:
- Extract latest chat history
- Rebuild TF-IDF model
- Update learned patterns in database

---

## View Generated Files

### Games
```
C:\Gamansai\ai\static\game_*.html
```

### 3D Models
```
C:\Gamansai\ai\static\models\model_*.glb
```

Download and open in:
- Blender
- Three.js Editor
- Online GLB viewers

---

## Response Priority (in order)

1. 🤖 **Trained Database** - Your 81 learned patterns
2. 🧠 **Feedback Learning** - Your 5-star rated responses
3. ✨ **Claude API** - Real AI (if key is set)
4. ⚙️ **Local Fallback** - Pattern matching

---

## Features at a Glance

| Feature | Status | Setup |
|---------|--------|-------|
| Real Games | ✅ | None |
| Real 3D Models | ✅ | None |
| Database Training | ✅ | None |
| Feedback Learning | ✅ | None |
| Claude API | ⚠️ | API key |

---

## Troubleshooting

### Server won't start
```bash
# Kill stale Python processes
pkill -f uvicorn

# Try again
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### Games won't generate
- Check `/c/Gamansai/ai/static/` exists
- Check Python can write to it

### 3D models won't download
- Check `/c/Gamansai/ai/static/models/` exists
- Try different browser

### Claude API not working
- Verify API key: `echo $ANTHROPIC_API_KEY`
- Get free key: https://console.anthropic.com
- Restart server after setting key

---

## That's It! 🎉

Your AI now has **real** features, not simulations.

Enjoy! 🚀
