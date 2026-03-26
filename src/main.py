from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

@app.route("/canva/callback")
def canva_callback():
    code = request.args.get("code")
    return f"Code received: {code}"

@app.route("/cmo")
def cmo():
    return "CMO AI çalışıyor 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)