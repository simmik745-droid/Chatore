"""
Keep Alive Server - Prevents bot from sleeping on free hosting services
"""

from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return """
    <h1>🍽️ Chatore Discord Bot</h1>
    <p>Bot is running successfully!</p>
    <p>Status: ✅ Online</p>
    <p>Powered by Gemini 2.5 Flash</p>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "chatore", "version": "1.0"}

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Start the keep-alive server in a separate thread"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Keep-alive server started on port 8080")