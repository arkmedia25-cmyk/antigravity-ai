from flask import Flask, request
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return "OK"

@app.route("/canva/callback")
def canva_callback():
    code = request.args.get("code")
    return f"Code received: {code}"

@app.route("/cmo")
def cmo():
    q = request.args.get("q", "Instagram için 3 kısa büyüme fikri ver")

    response = client.responses.create(
        model="gpt-4o-mini",
        input=q
    )

    return response.output_text

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)