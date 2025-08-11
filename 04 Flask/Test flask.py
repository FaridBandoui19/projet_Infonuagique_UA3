# Version 04

# 03 Serveur Flask.py
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from tenacity import retry, wait_exponential, stop_after_attempt

# 1) Chargement de la clé
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2) Aides pour gérer l'erreur 429
def is_quota_error(e: Exception) -> bool:
    return "insufficient_quota" in str(e).lower() or "quota" in str(e).lower()

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def call_openai(messages, temperature=0.2, model="gpt-4o-mini"):
    try:
        return client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
        )
    except RateLimitError as e:
        # Si c'est un manque de crédits -> ne pas réessayer
        if is_quota_error(e):
            raise
        # Sinon, laisser Tenacity réessayer (rate limit momentané)
        raise

# 3) Mini appli Flask
app = Flask(__name__)

@app.get("/")
def home():
    # Petite page de test
    return """
    <html><body>
      <h1>Test Chatbot</h1>
      <form method="post" action="/chatbot">
        <input name="message" placeholder="Votre message" />
        <button type="submit">Envoyer</button>
      </form>
      <p>Ou fais un POST JSON sur /chatbot avec {"message": "texte"}.</p>
    </body></html>
    """

@app.post("/chatbot")
def chatbot():
    # Récupère le message (JSON ou formulaire)
    if request.is_json:
        user_msg = (request.json or {}).get("message", "")
    else:
        user_msg = request.form.get("message", "")

    if not user_msg.strip():
        return jsonify(ok=False, error="Message vide"), 400

    try:
        resp = call_openai([
            {"role": "system", "content": "Tu es un assistant utile."},
            {"role": "user", "content": user_msg},
        ])
        reply = resp.choices[0].message.content
        return jsonify(ok=True, reply=reply)

    except RateLimitError as e:
        # <-- C’est ICI qu’on renvoie un vrai 429
        if is_quota_error(e):
            return jsonify(ok=False, error="Crédits API insuffisants (insufficient_quota)."), 429
        return jsonify(ok=False, error="Trop de requêtes. Réessaie dans un instant."), 429

    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

if __name__ == "__main__":
    # Lance le serveur
    app.run(debug=True)
