import os
from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
import httpx

app = Flask(__name__)

# --- NASTAVENÍ API ---
# Hodnoty se načtou z prostředí (v lokálu ze souboru .env)
api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL")

# Inicializace klienta (vypínáme ověřování certifikátu podle tvého návodu)
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    http_client=httpx.Client(verify=False)
)

# Simulovaná databáze vzkazů v paměti
messages = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_text = request.form.get("content")
        if user_text:
            # Volání AI pro vylepšení vzkazu
            response = client.chat.completions.create(
                model="gemma3:27b",
                messages=[
                    {"role": "system", "content": "Jsi asistent na nástěnce. Udělej vzkaz vtipnější nebo stručnější."},
                    {"role": "user", "content": user_text}
                ]
            )
            ai_text = response.choices[0].message.content
            messages.append({"original": user_text, "ai": ai_text})
        return redirect(url_for("index"))
    
    return render_template("index.html", messages=messages)

if __name__ == "__main__":
    # DŮLEŽITÉ: Port podle bodu 3 ve tvém návodu
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)