#!/bin/bash
set -e

mkdir -p ai_tv_show_studio/modules
mkdir -p ai_tv_show_studio/api
mkdir -p ai_tv_show_studio/data/media/show_videos
mkdir -p ai_tv_show_studio/data/media/show_logos
mkdir -p ai_tv_show_studio/data/media/show_music
mkdir -p ai_tv_show_studio/data/transcripts

cat > ai_tv_show_studio/requirements.txt <<'EOF'
streamlit
requests
python-dotenv
Pillow
EOF

cat > ai_tv_show_studio/installer.sh <<'EOF'
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Setup complete. Activate your venv with 'source venv/bin/activate' and run 'streamlit run app.py'"
EOF
chmod +x ai_tv_show_studio/installer.sh

cat > ai_tv_show_studio/.env.example <<'EOF'
VEO_API_KEY=your_veo_key_here
SUNO_API_KEY=your_suno_key_here
OPENAI_API_KEY=your_openai_key_here
EOF

cat > ai_tv_show_studio/app.py <<'EOF'
import streamlit as st
import os
import json
from modules import theme_selector, scene_engine, gallery, music, logo, transcript

DATA_DIR = "data"
SHOWS_FILE = os.path.join(DATA_DIR, "shows.json")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "media/show_videos"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "media/show_logos"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "media/show_music"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "transcripts"), exist_ok=True)

def load_shows():
    if not os.path.exists(SHOWS_FILE):
        with open(SHOWS_FILE, "w") as f:
            json.dump({}, f)
    with open(SHOWS_FILE, "r") as f:
        return json.load(f)

def save_shows(shows):
    with open(SHOWS_FILE, "w") as f:
        json.dump(shows, f, indent=2)

if "shows" not in st.session_state:
    st.session_state["shows"] = load_shows()

st.sidebar.title("AI TV Show Studio")
show_list = list(st.session_state["shows"].keys())
selected_show = st.sidebar.selectbox("Select Show", options=["Create New Show"] + show_list)
if selected_show != "Create New Show":
    selected_season = st.sidebar.number_input("Season", 1, 99, 1)
    selected_episode = st.sidebar.number_input("Episode", 1, 999, 1)
else:
    selected_season = None
    selected_episode = None

if st.sidebar.button("Show Media Gallery"):
    gallery.show_media_gallery()

if selected_show != "Create New Show" and st.sidebar.button("Generate Logo"):
    logo.generate_logo(selected_show)

if selected_show != "Create New Show" and st.sidebar.button("Create Show Music"):
    music.generate_music(selected_show)

if selected_show != "Create New Show" and st.sidebar.button("Save Transcript"):
    transcript.save_transcript(selected_show, selected_season, selected_episode)

if selected_show == "Create New Show":
    st.title("Create a New Show")
    theme_selector.theme_grid(st.session_state)
    if "new_show" in st.session_state:
        st.success(f"Show '{st.session_state['new_show']}' created!")
else:
    st.title(f"{selected_show} - S{selected_season}E{selected_episode}")
    scene_engine.display_scene_builder(selected_show, selected_season, selected_episode, st.session_state)

save_shows(st.session_state["shows"])
EOF

cat > ai_tv_show_studio/modules/theme_selector.py <<'EOF'
import streamlit as st

THEMES = {
    "Dating": [
        {"name": "Love Is Blind", "desc": "Contestants date and get engaged sight unseen, revealing chaos."},
        {"name": "The Bachelor", "desc": "One person dates many, with weekly dramatic eliminations."},
        {"name": "Newlyweds Game", "desc": "Couples answer spicy questions and get points for matching answers."}
    ],
    "Survival": [
        {"name": "Survivor", "desc": "Contestants compete for survival and alliances on a remote island."},
        {"name": "Naked and Afraid", "desc": "Strangers survive in the wild with no supplies. Awkwardness = 11/10."}
    ],
    "Trashy TV": [
        {"name": "Jersey Shore", "desc": "Party, drama, and questionable life choices."},
        {"name": "Flavor of Love", "desc": "Celebs look for love in absurd settings."}
    ]
}

def theme_grid(session_state):
    st.markdown("### Pick a Genre and Show Style")
    genre = st.selectbox("Genre", list(THEMES.keys()))
    shows = THEMES[genre]
    chosen_styles = []
    cols = st.columns(len(shows))
    for idx, show in enumerate(shows):
        with cols[idx]:
            c = st.checkbox(show["name"], key=f"showstyle_{genre}_{show['name']}")
            st.caption(show["desc"])
            if c:
                chosen_styles.append(show["name"])
    if st.button("Continue with selection"):
        session_state["theme"] = genre
        session_state["style"] = chosen_styles
        session_state["step"] = "show_details"
        show_details_form(session_state)

    if session_state.get("step") == "show_details":
        show_details_form(session_state)

def show_details_form(session_state):
    with st.form("show_details"):
        show_name = st.text_input("Show Name")
        drama_level = st.slider("Drama Level", 1, 10, 5)
        cast_names = st.text_area("Cast Names (comma separated)", "Alex, Jamie, Taylor")
        behaviors = st.multiselect("Behavioral Traits", ["Emotional", "Aggressive", "Comedic", "Scheming", "Shy", "Bold"])
        submitted = st.form_submit_button("Create Show")
        if submitted:
            show_id = show_name.strip().replace(" ", "_")
            session_state["shows"][show_id] = {
                "name": show_name,
                "theme": session_state["theme"],
                "style": session_state["style"],
                "drama": drama_level,
                "cast": [n.strip() for n in cast_names.split(",")],
                "behaviors": behaviors,
                "seasons": {}
            }
            session_state["new_show"] = show_name
            session_state["step"] = None
EOF

cat > ai_tv_show_studio/modules/scene_engine.py <<'EOF'
import streamlit as st
from api import veo

def display_scene_builder(show, season, episode, session_state):
    show_data = session_state["shows"][show]
    seasons = show_data.setdefault("seasons", {})
    episodes = seasons.setdefault(str(season), {})
    ep_data = episodes.setdefault(str(episode), {"scenes": [], "transcript": []})

    st.header("Scene Composer")
    st.write(f"Show: {show_data['name']} | Season: {season} | Episode: {episode}")

    if ep_data["scenes"]:
        st.video(ep_data["scenes"][-1]["video_path"])
        st.write("Last Scene:")
        st.write(ep_data["scenes"][-1]["prompt"])
    else:
        st.info("No scenes yet.")

    st.subheader("Compose Next Scene")
    scene_prompt = st.text_area("Describe what happens next (leave blank to randomize)", "")
    character_choices = st.multiselect("Choose active characters", show_data["cast"], default=show_data["cast"])
    if st.button("Generate Scene"):
        prompt = scene_prompt if scene_prompt else veo.random_scene_prompt(show_data, character_choices)
        video_path = veo.generate_scene(prompt, show, season, episode)
        new_scene = {"prompt": prompt, "video_path": video_path}
        ep_data["scenes"].append(new_scene)
        ep_data["transcript"].append(prompt)
        st.success("Scene generated!")
        st.experimental_rerun()
    if st.button("End Show"):
        veo.create_intro_and_transitions(show, season, episode)
        st.success("Show completed. Intro and transitions generated.")
EOF

cat > ai_tv_show_studio/modules/gallery.py <<'EOF'
import streamlit as st
import os

DATA_DIR = "data"

def show_media_gallery():
    st.title("Media Gallery")
    tabs = st.tabs(["Videos", "Music", "Logos", "Transcripts"])
    with tabs[0]:
        videos = os.listdir(os.path.join(DATA_DIR, "media/show_videos"))
        for v in videos:
            st.video(os.path.join(DATA_DIR, "media/show_videos", v))
    with tabs[1]:
        music = os.listdir(os.path.join(DATA_DIR, "media/show_music"))
        for m in music:
            st.audio(os.path.join(DATA_DIR, "media/show_music", m))
    with tabs[2]:
        logos = os.listdir(os.path.join(DATA_DIR, "media/show_logos"))
        for l in logos:
            st.image(os.path.join(DATA_DIR, "media/show_logos", l))
    with tabs[3]:
        transcripts = os.listdir(os.path.join(DATA_DIR, "transcripts"))
        for t in transcripts:
            st.markdown(f"**{t}**")
            with open(os.path.join(DATA_DIR, "transcripts", t), "r") as f:
                st.text(f.read())

def show_show_overview(selected_show):
    st.subheader(f"Overview for {selected_show}")
    st.write("This show is ready for new episodes or scene creation.")

def add_new_episode(show, season, episode):
    st.info("Episodes auto-create on use.")
EOF

cat > ai_tv_show_studio/modules/music.py <<'EOF'
import streamlit as st
from api import suno
import os

def generate_music(show):
    st.info("Generating theme music...")
    music_file = suno.create_theme_music(show)
    st.audio(music_file)
    st.success(f"Music saved: {music_file}")
EOF

cat > ai_tv_show_studio/modules/logo.py <<'EOF'
import streamlit as st
from api import openai_logo
import os

def generate_logo(show):
    st.info("Generating logo...")
    logo_file = openai_logo.create_logo(show)
    st.image(logo_file)
    st.success(f"Logo saved: {logo_file}")
EOF

cat > ai_tv_show_studio/modules/transcript.py <<'EOF'
import streamlit as st
import os

DATA_DIR = "data"

def save_transcript(show, season, episode):
    transcript_path = os.path.join(DATA_DIR, "transcripts", f"{show}_S{season}E{episode}.txt")
    from app import st
    shows = st.session_state["shows"]
    scenes = shows[show]["seasons"][str(season)][str(episode)]["transcript"]
    with open(transcript_path, "w") as f:
        for line in scenes:
            f.write(line + "\n")
    st.success(f"Transcript saved to {transcript_path}")
EOF

cat > ai_tv_show_studio/api/veo.py <<'EOF'
import os
import random

def random_scene_prompt(show_data, characters):
    char_str = ", ".join(characters)
    themes = [
        f"{char_str} get into a heated argument about a lost item.",
        f"{char_str} try to form a secret alliance.",
        f"{char_str} discover a mysterious envelope."
    ]
    return random.choice(themes)

def generate_scene(prompt, show, season, episode):
    video_file = f"data/media/show_videos/{show}_S{season}E{episode}_scene{random.randint(1,10000)}.mp4"
    open(video_file, "a").close()
    return video_file

def create_intro_and_transitions(show, season, episode):
    intro_file = f"data/media/show_videos/{show}_S{season}E{episode}_intro.mp4"
    open(intro_file, "a").close()
    return intro_file
EOF

cat > ai_tv_show_studio/api/suno.py <<'EOF'
import os

def create_theme_music(show):
    music_file = f"data/media/show_music/{show}_theme.mp3"
    open(music_file, "a").close()
    return music_file
EOF

cat > ai_tv_show_studio/api/openai_logo.py <<'EOF'
import os

def create_logo(show):
    logo_file = f"data/media/show_logos/{show}_logo.png"
    open(logo_file, "a").close()
    return logo_file
EOF

echo 'DONE. Your ai_tv_show_studio/ project is fully created!'
