import streamlit as st
import os
import json
from modules import theme_selector, scene_engine, gallery, music, logo, transcript
from youtube import auth, upload, playlist
import requests

# Set wide layout
st.set_page_config(layout="wide")

st.image("res/prompTV_streamlit_Banner23.png", use_container_width=True)

st.sidebar.image("res/prompTV2.png")

# --- Data paths ---
DATA_DIR = "data"
SHOWS_FILE = os.path.join(DATA_DIR, "shows.json")
UPLOADS_FILE = os.path.join(DATA_DIR, "uploads.json")

# --- Ensure all folders/files exist ---
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "media/show_videos"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "media/show_logos"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "media/show_music"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "transcripts"), exist_ok=True)

if not os.path.exists(SHOWS_FILE):
    with open(SHOWS_FILE, "w") as f:
        json.dump({}, f)
if not os.path.exists(UPLOADS_FILE):
    with open(UPLOADS_FILE, "w") as f:
        json.dump({}, f)

# --- Helper: Load shows/uploads ---
def load_shows():
    with open(SHOWS_FILE, "r") as f:
        return json.load(f)

def save_shows(shows):
    with open(SHOWS_FILE, "w") as f:
        json.dump(shows, f, indent=2)

def load_uploads():
    with open(UPLOADS_FILE, "r") as f:
        return json.load(f)

def save_uploads(uploads):
    with open(UPLOADS_FILE, "w") as f:
        json.dump(uploads, f, indent=2)

if "shows" not in st.session_state:
    st.session_state["shows"] = load_shows()
if "uploads" not in st.session_state:
    st.session_state["uploads"] = load_uploads()

# --- Fan Ideas (from Twitter microservice) ---
def fetch_fan_ideas():
    try:
        r = requests.get("http://twitter:8600/ideas", timeout=2)
        return r.json()
    except Exception:
        return []

fan_ideas = fetch_fan_ideas()
if fan_ideas:
    st.sidebar.subheader("Fan Scene Ideas")
    for idx, idea in enumerate(fan_ideas[-5:]):
        st.sidebar.markdown(
            f"- {idea['idea']} (#{idea['show']} S{idea['season']} E{idea['episode']})",
            unsafe_allow_html=True,
            key=f"fan_idea_{idx}",
        )

# --- Main Show Selection ---
st.sidebar.title("AI TV Show Studio")
show_list = list(st.session_state["shows"].keys())
selected_show = st.sidebar.selectbox(
    "Select Show",
    options=["Create New Show"] + show_list,
    key="studio_show_select"
)
if selected_show != "Create New Show":
    selected_season = st.sidebar.number_input(
        "Season", 1, 99, 1, key="studio_season"
    )
    selected_episode = st.sidebar.number_input(
        "Episode", 1, 999, 1, key="studio_episode"
    )
else:
    selected_season = None
    selected_episode = None

# --- Show Studio Actions (no duplicate buttons) ---
if st.sidebar.button("Show Media Gallery", key="show_gallery_studio"):
    gallery.show_media_gallery()

if selected_show != "Create New Show":
    if st.sidebar.button("Generate Logo", key="generate_logo_studio"):
        logo.generate_logo(selected_show)
    if st.sidebar.button("Create Show Music", key="create_music_studio"):
        music.generate_music(selected_show)
    if st.sidebar.button("Save Transcript", key="save_transcript_studio"):
        transcript.save_transcript(selected_show, selected_season, selected_episode)

# --- Main UI: Show builder or Create New Show ---
if selected_show == "Create New Show":
    st.info("Create a New Show - Pick a `Genre` and an optional `Show Style`")
    theme_selector.theme_grid(st.session_state)
    if "new_show" in st.session_state:
        st.success(f"Show '{st.session_state['new_show']}' created!")
else:
    st.title(f"{selected_show} - S{selected_season}E{selected_episode}")
    scene_engine.display_scene_builder(
        selected_show, selected_season, selected_episode, st.session_state
    )

save_shows(st.session_state["shows"])

# --- YouTube Channel Automation Sidebar Section ---
st.sidebar.markdown("---")
st.sidebar.title("YouTube Channel Automation")
st.sidebar.image("res/YT_sidebar.png")

yt_show_list = list(st.session_state["shows"].keys())
yt_selected_show = st.sidebar.selectbox(
    "YouTube: Select Show", yt_show_list, key="yt_show_select"
)
yt_selected_season = st.sidebar.number_input(
    "YouTube: Season", 1, 99, 1, key="yt_season"
)
yt_seasons = st.session_state["shows"].get(yt_selected_show, {}).get("seasons", {})
yt_episodes = yt_seasons.get(str(yt_selected_season), {})
yt_episode_numbers = [int(ep) for ep in yt_episodes.keys()] if yt_episodes else []
yt_selected_episode = st.sidebar.selectbox(
    "YouTube: Episode", yt_episode_numbers, key="yt_episode"
) if yt_episode_numbers else 1

if st.sidebar.button("Upload Episode to YouTube", key="yt_upload_button"):
    st.info("Uploading, please wait...")
    show_data = st.session_state["shows"][yt_selected_show]
    ep_data = yt_episodes.get(str(yt_selected_episode), {})
    if not ep_data:
        st.error("No episode data found.")
    else:
        title = f"{yt_selected_show} - S{yt_selected_season}E{yt_selected_episode}"
        description = "\n".join(ep_data.get("transcript", []))
        video_path = ep_data.get("scenes", [{}])[-1].get("video_path", "")
        transcript_txt = "\n".join(ep_data.get("transcript", []))
        creds = auth.get_youtube_credentials()
        video_id = upload.upload_video(creds, title, description, video_path)
        playlist_id = playlist.get_or_create_playlist(creds, yt_selected_show)
        playlist.add_video_to_playlist(creds, playlist_id, video_id)
        st.session_state["uploads"].setdefault(yt_selected_show, {}).setdefault(str(yt_selected_season), {})[str(yt_selected_episode)] = {
            "video_id": video_id,
            "playlist_id": playlist_id,
            "title": title,
            "description": description
        }
        save_uploads(st.session_state["uploads"])
        st.success(f"Uploaded: https://youtu.be/{video_id}")

if st.sidebar.button("Show Uploaded Episodes", key="yt_show_gallery"):
    gallery.show_gallery(st.session_state["uploads"])

# --- Main Content for YouTube Automation ---
st.sidebar.caption("""
Select a show, season, and episode, then upload it to your channel and organized playlist.  
Every episode is organized automatically into playlists matching your show titles.
""")
