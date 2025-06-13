import os
import json
import re
import tweepy
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_ACCOUNT = os.getenv("TWITTER_ACCOUNT")  # e.g. yourAIshowrunner (no @)
DATA_FILE = "data/twitter_scenes.json"

# Ensure data dir exists
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

client = tweepy.Client(bearer_token=BEARER_TOKEN)

def extract_metadata_from_tweet(text):
    # Extract hashtags as show, season, episode, characters
    hashtags = re.findall(r"#\w+", text)
    show = None
    season = None
    episode = None
    characters = []
    for tag in hashtags:
        tag_lower = tag.lower()
        if tag_lower.startswith("#season"):
            try:
                season = int(re.sub("[^0-9]", "", tag_lower))
            except Exception:
                continue
        elif tag_lower.startswith("#episode"):
            try:
                episode = int(re.sub("[^0-9]", "", tag_lower))
            except Exception:
                continue
        elif show is None:
            show = tag[1:]
        else:
            characters.append(tag[1:])
    return show, season, episode, characters

def process_tweets():
    # Load last processed tweet id
    last_id_file = "data/twitter_last_id.txt"
    if os.path.exists(last_id_file):
        with open(last_id_file, "r") as f:
            since_id = f.read().strip()
    else:
        since_id = None

    # Get mentions timeline
    mentions = client.get_users_mentions(id=client.get_user(username=TWITTER_ACCOUNT).data.id,
                                         since_id=since_id, max_results=100)
    if not mentions.data:
        print("No new mentions.")
        return

    new_scenes = []
    max_id = None
    for tweet in mentions.data:
        show, season, episode, characters = extract_metadata_from_tweet(tweet.text)
        idea = re.sub(r"#\w+", "", tweet.text).strip()
        scene_obj = {
            "tweet_id": tweet.id,
            "user": tweet.author_id,
            "show": show,
            "season": season,
            "episode": episode,
            "characters": characters,
            "idea": idea,
            "raw": tweet.text
        }
        new_scenes.append(scene_obj)
        if max_id is None or int(tweet.id) > int(max_id):
            max_id = tweet.id

    # Append to data file
    with open(DATA_FILE, "r") as f:
        scenes = json.load(f)
    scenes.extend(new_scenes)
    with open(DATA_FILE, "w") as f:
        json.dump(scenes, f, indent=2)

    # Save last processed id
    if max_id:
        with open(last_id_file, "w") as f:
            f.write(str(max_id))
    print(f"Processed {len(new_scenes)} new fan scene ideas.")

if __name__ == "__main__":
    process_tweets()
