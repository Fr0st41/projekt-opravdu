import os
from flask import Flask, request, render_template_string, redirect, url_for
from openai import OpenAI
import httpx

app = Flask(__name__)

# --- NASTAVENÍ API ---
api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL")

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    http_client=httpx.Client(verify=False)
)

messages = []

# --- HTML ŠABLONA PŘÍMO V KÓDU ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Nástěnka</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; color: white; padding: 40px; }
        .container { max-width: 800px; margin: auto; }
        form { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
        input { width: 70%; padding: 10px; border-radius: 4px; border: none; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .board { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
        .note { background: #fff176; color: #333; padding: 15px; border-radius: 2px; box-shadow: 5px 5px 10px rgba(0,0,0,0.5); transform: rotate(-1deg); }
        .note:nth-child(even) { transform: rotate(2deg); background: #cfd8dc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Nástěnka 🚀</h1>
        <form method="POST">
            <input type="text" name="content" placeholder="Napiš vzkaz..." required>
            <button type="submit">Přidat</button>
        </form>
        <div class="board">
            {% for m in messages %}
                <div class="note">
                    <p>{{ m.ai }}</p>
                </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_text = request.form.get("content")
        if user_text:
            try:
                response = client.chat.completions.create(
                    model="gemma3:27b",
                    messages=[
                        {"role": "system", "content": "Jsi vtipný asistent. Přetvoř vzkaz na nástěnku, aby byl krátký a úderný."},
                        {"role": "user", "content": user_text}
                    ]
                )
                ai_text = response.choices[0].message.content
                messages.append({"ai": ai_text})
            except Exception as e:
                messages.append({"ai": f"Chyba API: {str(e)}"})
        return redirect(url_for("index"))
    
    return render_template_string(HTML_TEMPLATE, messages=messages)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
