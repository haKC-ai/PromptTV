import os
import threading
import time
import json
from fastapi import FastAPI
from watcher import process_tweets

DATA_FILE = "data/twitter_scenes.json"
POLL_INTERVAL = int(os.getenv("TWITTER_POLL_SECONDS", "300"))  # every 5 min

app = FastAPI()

# Background polling thread
def poller():
    while True:
        try:
            process_tweets()
        except Exception as e:
            print("Polling error:", e)
        time.sleep(POLL_INTERVAL)

threading.Thread(target=poller, daemon=True).start()

@app.get("/ideas")
def get_ideas():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)
