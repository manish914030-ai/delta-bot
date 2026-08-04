import os
from threading import Thread
from flask import Flask
from main import run

app = Flask(__name__)

@app.route("/")
def home():
    return "Delta Bot is Running"

def start_bot():
    run()

Thread(target=start_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
