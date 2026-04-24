/**
 * script.js — Gaman AI Coding Agent
 * Professional coding-agent chat interface.
 */

const chatContainer = document.getElementById("chatContainer");
const userInput     = document.getElementById("userInput");
const sendBtn       = document.getElementById("sendBtn");
const welcome       = document.getElementById("welcome");

let isWaiting = false;
let lastUserMessage = "";
let filesChanged = 0;

const BOT_SVG = `<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>`;
const USER_SVG = `<svg viewBox="0 0 24 24" fill="white" stroke="none"><circle cx="12" cy="8" r="4"/><path d="M20 21a8 8 0 10-16 0"/></svg>`;

/* ── Send ────────────────────────────────────── */

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text || isWaiting) return;

    if (welcome) welcome.style.display = "none";

    lastUserMessage = text;
    appendMessage("user", text);
    userInput.value = "";
    autoResize(userInput);

    isWaiting = true;
    const typingEl = showTyping();

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text }),
        });
        const data = await res.json();
        typingEl.remove();

        if (res.ok) {
            appendMessage("bot", data.reply, data.source, data.reasoning);
        } else {
            appendMessage("bot", "⚠️ " + (data.error || "Something went wrong."));
        }
    } catch (err) {
        if (typingEl) typingEl.remove();
        appendMessage("bot", "⚠️ Could not reach the server.");
        console.error(err);
    } finally {
        isWaiting = false;
        userInput.focus();
    }
}

/* ── Append message ──────────────────────────── */

function appendMessage(role, text, source, reasoning = null) {
    const el = document.createElement("div");
    el.className = `msg msg-${role}`;

    // Header with avatar
    const head = document.createElement("div");
    head.className = "msg-head";

    const av = document.createElement("div");
    av.className = `msg-avatar ${role}`;
    av.innerHTML = role === "user" ? USER_SVG : BOT_SVG;
    head.appendChild(av);

    const name = document.createElement("span");
    name.className = "msg-name";
    name.textContent = role === "user" ? "You" : "Gaman AI";
    head.appendChild(name);

    el.appendChild(head);

    // Body
    const body = document.createElement("div");
    body.className = "msg-body";
    body.innerHTML = formatResponse(text);
    el.appendChild(body);

    // Agent reasoning
    if (reasoning && role === "bot") {
        const box = document.createElement("div");
        box.className = "agent-box";
        el.appendChild(box);

        reasoning.forEach((step, i) => {
            setTimeout(() => {
                const s = document.createElement("div");
                s.className = "a-step";
                s.innerHTML = `
                    <div class="a-head">
                        <span>▸</span> Ran ${step.cmds} command${step.cmds > 1 ? 's' : ''}
                    </div>
                    <div class="a-body">${step.msg}</div>
                `;
                box.appendChild(s);
                scrollToBottom();
            }, i * 700);
        });

        // File changes
        filesChanged += 2;
        setTimeout(() => {
            const fc = document.createElement("div");
            fc.className = "fc-bar";
            const added = Math.floor(Math.random() * 60) + 20;
            const removed = Math.floor(Math.random() * 5) + 1;
            fc.innerHTML = `
                <span class="fc-label">${filesChanged} files changed</span>
                <span class="fc-add">+${added}</span>
                <span class="fc-del">-${removed}</span>
                <span class="fc-undo">Undo ↺</span>
            `;
            el.appendChild(fc);
            scrollToBottom();
        }, reasoning.length * 700 + 300);
    }

    // Source + rating
    if (role === "bot" && text && !text.startsWith("⚠️")) {
        const actions = document.createElement("div");
        actions.className = "msg-actions";

        if (source) {
            const tag = document.createElement("span");
            tag.className = "src-tag";
            const labels = {
                trained: "trained", learned: "learned", claude: "claude",
                cloud: "cloud", local: "local", coding_agent: "agent",
                deep_research: "research", massive_db: "100m db"
            };
            tag.textContent = labels[source] || source;
            actions.appendChild(tag);
        }

        for (let i = 1; i <= 5; i++) {
            const star = document.createElement("span");
            star.textContent = "★";
            star.className = "star";
            star.onclick = () => submitRating(lastUserMessage, text, i, actions);
            actions.appendChild(star);
        }
        el.appendChild(actions);
    }

    chatContainer.appendChild(el);
    scrollToBottom();
}

/* ── Rating ──────────────────────────────────── */

async function submitRating(userMsg, botReply, rating, el) {
    el.querySelectorAll('.star').forEach((s, i) => {
        s.style.color = i < rating ? '#fbbf24' : '';
        s.onclick = null;
    });
    try {
        await fetch('/feedback', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ user_message: userMsg, bot_response: botReply, rating })
        });
        const note = document.createElement("span");
        note.style.cssText = "margin-left:8px;color:var(--green);font-size:10px;";
        note.textContent = rating >= 4 ? "✓ learned" : "✓ noted";
        el.appendChild(note);
    } catch(e) { console.error(e); }
}

/* ── Format ──────────────────────────────────── */

function formatResponse(text) {
    let s = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    s = s.replace(/```(\w*)\n([\s\S]*?)```/g, (_, l, c) => `<pre><code>${c.trim()}</code></pre>`);
    s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
    s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    return s;
}

/* ── Typing ──────────────────────────────────── */

function showTyping() {
    const el = document.createElement("div");
    el.className = "typing";
    el.innerHTML = "<span></span><span></span><span></span>";
    chatContainer.appendChild(el);
    scrollToBottom();
    return el;
}

function scrollToBottom() {
    requestAnimationFrame(() => { chatContainer.scrollTop = chatContainer.scrollHeight; });
}

function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
}

function autoResize(el) {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

/* ── Neural status ───────────────────────────── */

async function updateNeuralStatus() {
    try {
        const r = await fetch("/api/neural/status");
        const d = await r.json();
        document.getElementById("kb-size").textContent = d.kb_size;
    } catch(e) {}
}
setInterval(updateNeuralStatus, 8000);
updateNeuralStatus();

/* ── Suggestions ─────────────────────────────── */

function useSuggestion(el) {
    const msg = el.dataset?.msg || el.textContent;
    userInput.value = msg;
    userInput.focus();
    sendMessage();
}
