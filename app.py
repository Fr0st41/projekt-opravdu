import os
import random
import base64
from datetime import datetime
from flask import Flask, request, render_template_string, redirect
from openai import OpenAI
import httpx

app = Flask(__name__)

# --- KONFIGURACE AI (Školní Kuřim API) ---
api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL")
MODEL_NAME = "gemma3:27b"

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    http_client=httpx.Client(verify=False) # Vypnutí ověřování SSL podle návodu
)

# --- DATABÁZE VZKAZŮ ---
messages_db = []
message_id_counter = 0
NOTE_COLORS = ["#fffacd", "#e0ffff", "#e6e6fa", "#ffdab9", "#d8f8d8", "#ffe4e1"]

def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Jsi užitečný a vtipný asistent na třídní nástěnce. Odpovídej stručně a jasně."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Promiň, spím nebo mám poruchu. (Chyba API: {str(e)})"

# --- VZHLED (HTML & CSS) ---
HTML_MAIN = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="utf-8">
    <title>Digitální Nástěnka 📌</title>
    <style>
        body { font-family: 'Comic Sans MS', cursive, sans-serif; margin: 0; padding: 20px; min-height: 100vh; background-color: #c19a6b; background-image: url('https://www.transparenttextures.com/patterns/cork-board.png'); }
        h1 { text-align: center; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.6); }
        .controls { text-align: center; margin-bottom: 30px; }
        .main-form { background: rgba(255,255,255,0.95); padding: 15px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .main-form input[type="text"] { padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-right: 5px; }
        .main-form input[type="file"] { margin-right: 10px; font-size: 0.9em; }
        .main-form button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .ai-btn { display: inline-block; margin-left: 15px; padding: 12px 20px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        
        .board { display: flex; flex-wrap: wrap; gap: 30px; justify-content: center; padding: 20px; }
        
        .sticky-note { width: 280px; min-height: 250px; padding: 25px 20px 10px 20px; box-shadow: 5px 5px 15px rgba(0,0,0,0.4); position: relative; display: flex; flex-direction: column; transition: transform 0.2s; }
        .sticky-note:nth-child(even) { transform: rotate(2deg); }
        .sticky-note:nth-child(odd) { transform: rotate(-2deg); }
        .sticky-note:hover { transform: rotate(0deg) scale(1.05); z-index: 10; }
        
        .sticky-note::before { content: ""; position: absolute; top: 10px; left: 50%; transform: translateX(-50%); width: 15px; height: 15px; background-color: #d9534f; border-radius: 50%; box-shadow: 1px 1px 3px rgba(0,0,0,0.5); }
        
        .meta { font-size: 0.8em; color: #555; border-bottom: 1px solid rgba(0,0,0,0.1); padding-bottom: 5px; margin-bottom: 10px; }
        .note-text { font-size: 1.1em; flex-grow: 1; word-wrap: break-word; font-weight: bold; color: #222; margin-bottom: 10px; }
        
        /* MAGIE PRO OBRÁZKY: Automatické formátování */
        .note-image { width: 100%; max-height: 180px; object-fit: cover; border-radius: 5px; margin-bottom: 10px; border: 1px solid rgba(0,0,0,0.2); box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
        
        .replies { margin-bottom: 15px; font-size: 0.9em; color: #333; }
        .reply-item { border-left: 2px solid rgba(0,0,0,0.3); padding-left: 8px; margin-bottom: 8px; background: rgba(255,255,255,0.3); border-radius: 0 5px 5px 0; padding: 5px; }
        .reply-meta { font-size: 0.75em; color: #666; font-style: italic; margin-bottom: 3px; }
        
        .reply-form { display: flex; gap: 5px; margin-top: auto; border-top: 1px dashed rgba(0,0,0,0.3); padding-top: 10px; }
        .reply-form input { flex-grow: 1; padding: 5px; border: 1px solid rgba(0,0,0,0.2); background: rgba(255,255,255,0.6); border-radius: 3px; font-family: inherit; width: 40%;}
        .reply-form button { padding: 5px 10px; background: #333; color: white; border: none; cursor: pointer; border-radius: 3px; }
    </style>
    
    <script>
        setInterval(function() {
            let activeTag = document.activeElement.tagName.toLowerCase();
            if (activeTag !== 'input' && activeTag !== 'textarea') {
                window.location.reload();
            }
        }, 5000); 
    </script>
</head>
<body>
    <h1>Třídní Nástěnka 📌</h1>
    <div class="controls">
        <form method="POST" action="/add" class="main-form" enctype="multipart/form-data">
            <input type="text" name="author" placeholder="Tvé jméno..." required style="width: 100px;">
            <input type="text" name="msg" placeholder="Napiš vzkaz... (@AI)" required style="width: 250px;">
            <input type="file" name="image" accept="image/*">
            <button type="submit">Připíchnout</button>
        </form>
        <a href="/ai" class="ai-btn">🤖 AI Poradna</a>
    </div>

    <div class="board">
        {% for msg in messages %}
            <div class="sticky-note" style="background-color: {{ msg.color }};">
                <div class="meta">👤 <b>{{ msg.author }}</b> | 🕒 {{ msg.timestamp }}</div>
                
                {% if msg.image %}
                    <img src="{{ msg.image }}" class="note-image" alt="Obrázek k vzkazu">
                {% endif %}
                
                <div class="note-text">{{ msg.text }}</div>
                
                <div class="replies">
                    {% for r in msg.replies %}
                        <div class="reply-item">
                            <div class="reply-meta">👤 <b>{{ r.author }}</b> | 🕒 {{ r.timestamp }}</div>
                            <div>{{ r.text }}</div>
                        </div>
                    {% endfor %}
                </div>
                
                <form method="POST" action="/reply" class="reply-form">
                    <input type="hidden" name="note_id" value="{{ msg.id }}">
                    <input type="text" name="reply_author" placeholder="Jméno..." required style="width: 30%;">
                    <input type="text" name="reply_text" placeholder="Odpověz..." required>
                    <button type="submit">↪</button>
                </form>
            </div>
        {% else %}
            <h2 style="color: white; text-align: center; width: 100%; text-shadow: 1px 1px 3px black;">Zatím tu nic není, buď první!</h2>
        {% endfor %}
    </div>
</body>
</html>
"""

HTML_AI = """<!DOCTYPE html><html lang="cs"><head><meta charset="utf-8"><title>AI Poradna</title><style>body { font-family: sans-serif; margin: 40px; background: #eef2f5; } .container { max-width: 600px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); } input { padding: 10px; width: 70%; border: 1px solid #ccc; border-radius: 5px; } button { padding: 10px 20px; background: #007BFF; color: white; border: none; border-radius: 5px; cursor: pointer; } .result { background: #f8f9fa; padding: 15px; border-left: 5px solid #007BFF; margin-top: 20px; } .error { background: #ffe6e6; padding: 15px; border-left: 5px solid #d9534f; margin-top: 20px; color: #a94442; }</style></head><body><div class="container"><h1 style="color: #007BFF; margin-top: 0;">Online AI Poradna 🤖</h1><form method="POST" action="/ai"><input type="text" name="query" placeholder="Zeptej se umělé inteligence..." required> <button type="submit">Odeslat</button></form><br><a href="/" style="font-weight: bold; color: #333; text-decoration: none;">⬅️ Zpět na Nástěnku</a>{% if answer %}<div class="result"><p><strong>Dotaz:</strong> {{ question }}</p><p><strong>AI:</strong> {{ answer }}</p></div>{% elif error %}<div class="error"><p><strong>Chyba:</strong> {{ error }}</p></div>{% endif %}</div></body></html>"""

# --- ROUTOVÁNÍ ---
@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_MAIN, messages=messages_db)

@app.route('/add', methods=['POST'])
def add_note():
    global message_id_counter
    author = request.form.get('author', 'Anonym')
    text = request.form.get('msg')
    
    # Zpracování nahraného obrázku
    file = request.files.get('image')
    img_b64 = None
    if file and file.filename:
        # Převedeme obrázek do textového formátu Base64, aby fungoval bez ukládání na disk
        img_b64 = "data:" + file.content_type + ";base64," + base64.b64encode(file.read()).decode('utf-8')
    
    if text:
        message_id_counter += 1
        new_note = {
            "id": message_id_counter,
            "author": author,
            "text": text,
            "color": random.choice(NOTE_COLORS),
            "timestamp": datetime.now().strftime("%H:%M"),
            "image": img_b64, # Uložíme obrázek k papírku
            "replies": []
        }
        messages_db.insert(0, new_note)

        if "@AI" in text.upper():
            prompt = text.replace("@AI", "").replace("@ai", "").strip()
            ai_reply = ask_ai(prompt if prompt else "Ahoj, představ se krátce.")
            new_note["replies"].append({
                "author": "🤖 AI Asistent",
                "text": ai_reply,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
    return redirect('/')

@app.route('/reply', methods=['POST'])
def add_reply():
    note_id = int(request.form.get('note_id'))
    author = request.form.get('reply_author', 'Anonym')
    reply_text = request.form.get('reply_text')
    
    if reply_text:
        for msg in messages_db:
            if msg["id"] == note_id:
                msg["replies"].append({
                    "author": author,
                    "text": reply_text,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
                if "@AI" in reply_text.upper():
                    prompt = reply_text.replace("@AI", "").replace("@ai", "").strip()
                    ai_reply = ask_ai(prompt if prompt else "Ahoj.")
                    msg["replies"].append({
                        "author": "🤖 AI Asistent",
                        "text": ai_reply,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                break
    return redirect('/')

@app.route('/ai', methods=['GET', 'POST'])
def ai_page():
    answer, question, error = None, None, None
    if request.method == 'POST':
        question = request.form.get('query')
        answer = ask_ai(question)
        if answer.startswith("Promiň"):
            error = answer
            answer = None
    return render_template_string(HTML_AI, question=question, answer=answer, error=error)

if __name__ == '__main__':
    # Správné načtení portu pro serverové nasazení
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
