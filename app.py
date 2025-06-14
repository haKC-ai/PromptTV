import streamlit as st

import os
import json
import pandas as pd
from moviepy import *
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.audio.fx.all import volumex
from moviepy.video.fx.all import resize
from moviepy.video.VideoClip import ImageClip
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.fx.all import volumex
from modules import theme_selector, scene_engine, gallery, music, logo, transcript
from youtube import auth, upload, playlist
from api import veo
from io import BytesIO
import tempfile
import glob
from modules import theme_selector
import openai
from dotenv import load_dotenv
import base64


st.set_page_config(
    page_title="PromptTV",
    page_icon="res/favicon.png",  # Path to your favicon (relative to script)
    layout="wide"
)

st.image("res/prompTV_streamlit_Banner23.png", use_container_width=True)
st.sidebar.image("res/prompTV2.png")

DATA_DIR = "data"
SHOWS_FILE = os.path.join(DATA_DIR, "shows.json")
UPLOADS_FILE = os.path.join(DATA_DIR, "uploads.json")

# --- Ensure folders/files exist ---
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "media/show_videos"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "media/show_logos"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "media/show_music"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "transcripts"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "shows"), exist_ok=True)

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)
def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

if not os.path.exists(SHOWS_FILE):
    save_json({}, SHOWS_FILE)
if not os.path.exists(UPLOADS_FILE):
    save_json({}, UPLOADS_FILE)
if "shows" not in st.session_state:
    st.session_state["shows"] = load_json(SHOWS_FILE)
if "uploads" not in st.session_state:
    st.session_state["uploads"] = load_json(UPLOADS_FILE)

# Utility paths
def get_shows_dir():
    return os.path.join("data", "shows")
def get_transcripts_dir(show):
    return os.path.join("data", "transcripts", show)
def get_prompts_dir(show):
    return os.path.join(get_shows_dir(), show, "veo_prompts")
def get_music_dir(show):
    return os.path.join(get_shows_dir(), show, "music_prompts")

# Use only shows that are BOTH in shows.json AND have a video directory for binge/galleries
shows_in_json = set(st.session_state["shows"].keys())
shows_in_videos = set([d for d in os.listdir("data/media/show_videos") if os.path.isdir(os.path.join("data/media/show_videos", d))]) if os.path.exists("data/media/show_videos") else set()
all_shows = sorted(list(shows_in_json | shows_in_videos))
enable_new_show = st.sidebar.checkbox("Click to create a new show", key="enable_create_show")
#theme_selector.theme_grid(st.session_state, enable_new_show)

# --- BingeWatch Sidebar (expander, not nested, bulletproof) ---
with st.sidebar.expander("BingeWatch", expanded=False):
    video_root = "data/media/show_videos"
    # Only list real show folders, and handle empty gracefully
    shows = sorted([d for d in os.listdir(video_root) if os.path.isdir(os.path.join(video_root, d))]) if os.path.exists(video_root) else []
    has_shows = len(shows) > 0

    # Only allow real shows to be selected
    show_display_list = shows if has_shows else []
    if not show_display_list:
        st.markdown("*No shows available yet. Create one in Show Tools.*")
        selected_show_bw = None
        selected_season_bw = None
        show_gallery_btn = None
    else:
        selected_show_bw = st.selectbox("Show", show_display_list, key="binge_show_select")
        # Get available seasons for the selected show
        show_dir = os.path.join(video_root, selected_show_bw)
        seasons = sorted([d for d in os.listdir(show_dir) if d.startswith("S") and os.path.isdir(os.path.join(show_dir, d))])
        season_display_list = [s.replace("S", "") for s in seasons] if seasons else []
        if not season_display_list:
            st.markdown("*No seasons available for this show.*")
            selected_season_bw = None
            show_gallery_btn = None
        else:
            selected_season_bw = st.selectbox("Season", season_display_list, key="binge_season_select")
            show_gallery_btn = st.button("Show Gallery", key="show_gallery_btn")

            # Only allow storing valid gallery selection if both are set
            if show_gallery_btn and selected_show_bw and selected_season_bw:
                st.session_state["binge_gallery"] = (selected_show_bw, selected_season_bw)



def generate_logo_for_show(selected_show_tools):
    # Prepare logo path
    logo_dir = os.path.join("data", "media", "show_logos")
    os.makedirs(logo_dir, exist_ok=True)
    logo_file = os.path.join(logo_dir, f"{selected_show_tools}_logo.png")

    # Collect vibe metadata
    meta_path = os.path.join("data", "shows", selected_show_tools, "metadata.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as mf:
            meta = json.load(mf)
    theme = meta.get("theme", "Vaporwave cyberpunk")
    style = meta.get("style", "")
    desc = meta.get("desc", "")
    vibe = f"Theme: {theme}. Style: {style}. Description: {desc}."

    prompt = (
        f"Design a bold, modern TV show logo for the series titled '{selected_show_tools}'. "
        f"The logo must prominently include the show title '{selected_show_tools}' as part of the design. "
        "Use a transparent background. Capture the exact vibe of the show. "
        f"{vibe} The graphic should feel realistic, professional, and striking, suitable for an actual streaming service. "
        "Use vaporwave and cyberpunk influences, but let the show's unique energy drive the look."
    )

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY not found in .env file.")
        return

    if st.button("Generate Logo", key="generate_logo_tools"):
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.responses.create(
                model="gpt-4o",
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
                    }
                ],
                text={"format": {"type": "text"}},
                reasoning={},
                tools=[
                    {
                        "type": "image_generation",
                        "size": "1024x1024",
                        "quality": "high",
                        "output_format": "png",
                        "background": "transparent",
                        "moderation": "auto",
                    }
                ],
                temperature=1,
                max_output_tokens=2048,
                top_p=1,
                store=True,
            )
            image_b64 = response.output[0].result
            img_bytes = BytesIO(base64.b64decode(image_b64))
            with open(logo_file, "wb") as f:
                f.write(img_bytes.getbuffer())
            img_bytes.seek(0)
            st.success(f"Logo generated and saved for {selected_show_tools}")
            #st.image(img_bytes, width=350, caption=f"{selected_show_tools} Logo")
            st.download_button(
                "Download Logo",
                img_bytes,
                file_name=os.path.basename(logo_file),
                mime="image/png",
                key=f"dl_logo_{selected_show_tools}_latest"
            )
            return img_bytes, logo_file
        except Exception as e:
            st.error(f"Logo generation failed: {e}")
            return None, None

    # If logo already exists, offer to display and download
    elif os.path.exists(logo_file):
        with open(logo_file, "rb") as lf:
            data = lf.read()
        img_bytes = BytesIO(data)
        #st.image(img_bytes, width=350, caption=f"{selected_show_tools} Logo")
        st.download_button(
            "Download Logo",
            img_bytes,
            file_name=os.path.basename(logo_file),
            mime="image/png",
            key=f"dl_logo_{selected_show_tools}_existing"
        )
        return img_bytes, logo_file

    else:
        st.info("No logo generated yet for this show.")
        return None, None

with st.sidebar.expander("Write", expanded=False):
    show_list = sorted([
        d for d in os.listdir(get_shows_dir())
        if os.path.isdir(os.path.join(get_shows_dir(), d))
    ])
    selected_show = st.selectbox("Show", show_list, key="write_show_select")
    season_list = []
    episode_list = []

    if selected_show:
        transcripts_dir = get_transcripts_dir(selected_show)
        os.makedirs(transcripts_dir, exist_ok=True)
        season_list = sorted([
            d.replace("S", "") for d in os.listdir(transcripts_dir)
            if d.startswith("S") and os.path.isdir(os.path.join(transcripts_dir, d))
        ])
    selected_season = st.selectbox("Season", season_list, key="write_season_select") if season_list else st.number_input("Season", min_value=1, step=1, key="write_season_input")

    episode_list = []
    if selected_show and selected_season:
        season_dir = os.path.join(transcripts_dir, f"S{selected_season}")
        os.makedirs(season_dir, exist_ok=True)
        episode_list = sorted([
            d.replace("E", "") for d in os.listdir(season_dir)
            if d.startswith("E") and os.path.isdir(os.path.join(season_dir, d))
        ])
    selected_episode = st.selectbox("Episode", episode_list, key="write_episode_select") if episode_list else st.number_input("Episode", min_value=1, step=1, key="write_episode_input")
    st.checkbox("Write Episode", key="write_episode_enable")


# --- Show Tools Sidebar (expander, not nested) ---
with st.sidebar.expander("Show Tools", expanded=False):
    show_list_tools = sorted([d for d in os.listdir(get_shows_dir()) if os.path.isdir(os.path.join(get_shows_dir(), d))])
    selected_show_tools = st.selectbox("Select Show", show_list_tools, key="tools_show_select")
    st.button("Show Media Gallery", key="show_gallery_tools")
    generate_logo_for_show(selected_show_tools)
    st.button("Generate Show Intro", key="generate_intro_tools")
    st.markdown("#### Generate Show Music")
    music_prompts_dir = get_music_dir(selected_show_tools)
    os.makedirs(music_prompts_dir, exist_ok=True)
    prompt_file = os.path.join(music_prompts_dir, "show_music_prompt.txt")
    just_prompt_music = st.checkbox("Just generate & save prompt (do not send to Suno)", key=f"just_save_music_prompt_{selected_show_tools}")
    if st.button("Generate Show Music", key=f"generate_music_btn_{selected_show_tools}"):
        show_meta_path = os.path.join(get_shows_dir(), selected_show_tools, "metadata.json")
        show_meta = {}
        if os.path.exists(show_meta_path):
            with open(show_meta_path, "r", encoding="utf-8") as mf:
                show_meta = json.load(mf)
        theme = show_meta.get("theme", "")
        style = show_meta.get("style", "")
        cast = show_meta.get("cast", [])
        behaviors = show_meta.get("behaviors", {})
        drama = show_meta.get("drama", 5)
        desc = ""
        try:
            from modules.theme_selector import THEMES
            style_names = [s for s in style] if isinstance(style, list) else [style]
            descs = []
            for t in theme if isinstance(theme, list) else [theme]:
                genre = t.split(" ", 1)[-1] if " " in t else t
                for showdef in THEMES.get(genre, []):
                    if showdef["name"] in style_names:
                        descs.append(showdef["desc"])
            desc = " ".join(descs)
        except Exception:
            desc = ""
        music_prompt = (
            f"Generate a catchy, original theme song for the TV show '{selected_show_tools}'.\n"
            f"Theme: {theme}\n"
            f"Style: {style}\n"
            f"Show Description: {desc}\n"
            f"Cast: {', '.join(cast)}\n"
            f"Behaviors: {json.dumps(behaviors)}\n"
            f"Drama Level: {drama}\n"
            "The music should capture the show's unique energy and set the tone for each episode. "
            "Lyrics and melody should reflect the personalities, drama, and comedic moments present in the show."
        )
        with open(prompt_file, "w", encoding="utf-8") as pf:
            pf.write(music_prompt)
        st.success(f"Music prompt saved to {prompt_file}")
        if not just_prompt_music:
            st.info("Suno upload integration is not active yet. You can use the prompt above with Suno manually.")

    show_prompts_check = st.checkbox("Enable Show Prompts, Transcripts, and Music display", key="enable_show_prompts")
    transcripts_dir = get_transcripts_dir(selected_show_tools)
    prompts_dir = get_prompts_dir(selected_show_tools)
    music_dir = get_music_dir(selected_show_tools)
    seasons = sorted([d for d in os.listdir(transcripts_dir) if d.startswith("S")]) if os.path.exists(transcripts_dir) else []
    episodes = []
    scenes = []
    selected_season_tools = None
    selected_episode_tools = None
    if seasons:
        selected_season_tools = st.selectbox("Season", seasons, key=f"transcript_season_select_{selected_show_tools}")
        episodes_dir = os.path.join(transcripts_dir, selected_season_tools)
        episodes = sorted([d for d in os.listdir(episodes_dir) if d.startswith("E")]) if os.path.exists(episodes_dir) else []
    if episodes:
        selected_episode_tools = st.selectbox("Episode", episodes, key=f"transcript_episode_select_{selected_show_tools}")
        scenes_dir = os.path.join(transcripts_dir, selected_season_tools, selected_episode_tools)
        scenes = sorted([f for f in os.listdir(scenes_dir) if f.startswith("scene_") and f.endswith(".txt")]) if os.path.exists(scenes_dir) else []
    prompts = []
    if os.path.exists(prompts_dir):
        for root, dirs, files in os.walk(prompts_dir):
            for fname in files:
                if fname.endswith(".txt"):
                    prompts.append(os.path.relpath(os.path.join(root, fname), prompts_dir))
    music_files = []
    if os.path.exists(music_dir):
        for f in os.listdir(music_dir):
            if f.endswith(".txt"):
                music_files.append(f)
    to_show_scenes = st.multiselect("Scenes to View", scenes, default=scenes[:1] if scenes else [], key=f"multiselect_scenes_{selected_show_tools}")
    to_show_prompts = st.multiselect("Prompts to View", prompts, default=prompts[:1] if prompts else [], key=f"multiselect_prompts_{selected_show_tools}")
    to_show_music = st.multiselect("Music to View", music_files, default=music_files[:1] if music_files else [], key=f"multiselect_music_{selected_show_tools}")
    st.session_state["show_tools_display"] = {
        "show": selected_show_tools,
        "season": selected_season_tools if seasons else None,
        "episode": selected_episode_tools if episodes else None,
        "scenes": to_show_scenes,
        "prompts": to_show_prompts,
        "music": to_show_music,
        "enabled": show_prompts_check
    }
with st.sidebar.expander("Create Videos", expanded=False):

    transcript_root = os.path.join("data", "transcripts")
    shows_dir = os.path.join("data", "shows")

    if os.path.exists(transcript_root):
        shows = sorted([
            d for d in os.listdir(transcript_root)
            if os.path.isdir(os.path.join(transcript_root, d))
        ])
        if shows:
            selected_show = st.selectbox("Show", shows, key="veo_show_select")
            seasons_path = os.path.join(transcript_root, selected_show)
            seasons = sorted([
                d for d in os.listdir(seasons_path)
                if d.startswith("S") and os.path.isdir(os.path.join(seasons_path, d))
            ]) if os.path.exists(seasons_path) else []
            if seasons:
                selected_season = st.selectbox("Season", seasons, key="veo_season_select")
                episodes_path = os.path.join(seasons_path, selected_season)
                episodes = sorted([
                    d for d in os.listdir(episodes_path)
                    if d.startswith("E") and os.path.isdir(os.path.join(episodes_path, d))
                ]) if os.path.exists(episodes_path) else []
                if episodes:
                    selected_episode = st.selectbox("Episode", episodes, key="veo_episode_select")
                    scenes_path = os.path.join(episodes_path, selected_episode)
                    scenes = sorted([
                        f for f in os.listdir(scenes_path)
                        if f.startswith("scene_") and f.endswith(".txt")
                    ]) if os.path.exists(scenes_path) else []
                    if scenes:
                        selected_scene = st.selectbox("Scene", scenes, key="veo_scene_select")

                        # Multiselect for previous scenes as context
                        context_scenes = st.multiselect(
                            "Include previous scenes for continuity context:",
                            scenes,
                            default=scenes[:-1] if len(scenes) > 1 else [],
                            key="veo_context_scenes"
                        )

                        just_prompt = st.checkbox(
                            "Just generate & save prompt (do not send to Veo)", 
                            key="just_save_veo_prompt"
                        )

                        if st.button("Send this scene to Veo", key="send_veo_btn"):
                            scene_file = os.path.join(scenes_path, selected_scene)
                            with open(scene_file, "r", encoding="utf-8") as f:
                                scene_text = f.read()

                            # Get text for context scenes in order
                            context_texts = []
                            for ctx in context_scenes:
                                ctx_path = os.path.join(scenes_path, ctx)
                                if os.path.exists(ctx_path):
                                    with open(ctx_path, "r", encoding="utf-8") as cf:
                                        context_texts.append(
                                            f"Scene {ctx.replace('scene_', '').replace('.txt','')}: {cf.read()}"
                                        )

                            # Load show metadata for full context if available
                            meta_path = os.path.join(shows_dir, selected_show, "metadata.json")
                            show_context = ""
                            if os.path.exists(meta_path):
                                with open(meta_path, "r", encoding="utf-8") as mf:
                                    meta = json.load(mf)
                                show_context = (
                                    f"Show Title: {meta.get('name', selected_show)}\n"
                                    f"Theme: {meta.get('theme')}\n"
                                    f"Styles: {meta.get('style')}\n"
                                    f"Cast: {', '.join(meta.get('cast', []))}\n"
                                    f"Traits: {json.dumps(meta.get('behaviors', {}))}\n"
                                    f"Drama Level: {meta.get('drama', 5)}\n"
                                )

                            prompt_text = (
                                f"{show_context}\n"
                                f"Season: {selected_season}, Episode: {selected_episode}\n"
                                f"CONTEXT:\n" + "\n\n".join(context_texts) + "\n"
                                f"CURRENT SCENE:\n{scene_text}\n"
                                "Generate a vivid, TV-ready video scene. Maintain perfect continuity and consistency with all previous scenes and character personalities."
                            )

                            # Directory for generated prompts/videos
                            prompt_dir = os.path.join(
                                shows_dir, selected_show, "veo_prompts", selected_season, selected_episode
                            )
                            os.makedirs(prompt_dir, exist_ok=True)

                            # Placeholder for generated video (matching binge watch logic)
                            show_videos_root = os.path.join(
                                "data", "media", "show_videos", selected_show, selected_season, selected_episode
                            )
                            os.makedirs(show_videos_root, exist_ok=True)

                            # Get scene number
                            scene_num = selected_scene.replace("scene_", "").replace(".txt", "")
                            placeholder_video = os.path.join(show_videos_root, f"scene_{scene_num}.mp4")

                            if not os.path.exists(placeholder_video):
                                with open(placeholder_video, "wb") as f:
                                    f.write(b"")

                            prompt_file = os.path.join(prompt_dir, f"{selected_scene}_prompt.txt")
                            with open(prompt_file, "w", encoding="utf-8") as pf:
                                pf.write(prompt_text)

                            if just_prompt:
                                st.success(f"Prompt saved to {prompt_file} (placeholder video created at {placeholder_video})")
                            else:
                                veo.generate_scene(
                                    prompt_text, selected_show, selected_season, selected_episode
                                )
                                st.success(f"Scene sent to Veo (placeholder video at {placeholder_video})")

                    else:
                        st.info("No scenes found for this episode.")
                else:
                    st.info("No episodes found for this season.")
            else:
                st.info("No seasons found for this show.")
        else:
            st.info("No shows found in transcript storage yet.")
    else:
        st.info("No shows found in transcript storage yet.")


# --- Utility functions ---
def get_shows_dir():
    return os.path.join("data", "shows")

def get_media_dir(show):
    return os.path.join("data", "media", "show_videos", show)

def get_logo_dir(show):
    return os.path.join("data", "media", "show_logos")

def get_music_dir(show):
    return os.path.join("data", "media", "show_music", show)

def get_production_dir(show):
    return os.path.join(get_shows_dir(), show, "production")

# --- Sidebar: Show Producer Expander ---
with st.sidebar.expander("Show Producer", expanded=False):
    show_list = sorted([
        d for d in os.listdir(get_shows_dir())
        if os.path.isdir(os.path.join(get_shows_dir(), d))
    ])
    selected_show = st.selectbox("Select Show", show_list, key="producer_show_select")
    enable_producer = st.checkbox("Produce this show", key="enable_produce")
    st.session_state["enable_producer"] = enable_producer

    # Only show upload controls if a show is selected
    if selected_show:
        # Upload new video clip
        st.markdown("##### Upload New Video")
        season_dirs = [
            d for d in os.listdir(get_media_dir(selected_show))
            if d.startswith("S") and os.path.isdir(os.path.join(get_media_dir(selected_show), d))
        ]
        season_dirs = sorted(season_dirs)
        if season_dirs:
            upload_season = st.selectbox("Upload To Season", [s.replace("S", "") for s in season_dirs], key="upload_video_season")
            video_file = st.file_uploader("Video File", type=["mp4", "mov", "webm", "avi", "mkv"], key="video_upload")
            if video_file:
                target_dir = os.path.join(get_media_dir(selected_show), f"S{upload_season}")
                os.makedirs(target_dir, exist_ok=True)
                save_path = os.path.join(target_dir, video_file.name)
                with open(save_path, "wb") as f:
                    f.write(video_file.read())
                st.success(f"Uploaded {video_file.name} to {target_dir}")
        else:
            st.info("No seasons found. Create a season first.")

        # Upload image overlay        # Upload image overlay
        st.markdown("##### Upload Logo/Image")
        image_file = st.file_uploader("Image File", type=["png", "jpg", "jpeg", "webp"], key="image_upload")
        if image_file is not None:
            logo_dir = get_logo_dir(selected_show)
            os.makedirs(logo_dir, exist_ok=True)
            save_path = os.path.join(logo_dir, image_file.name)
            with open(save_path, "wb") as f:
                f.write(image_file.read())
            st.success(f"Uploaded {image_file.name} to {logo_dir}")



        # Upload music
        st.markdown("##### Upload Music")
        music_file = st.file_uploader("Music File", type=["mp3", "wav", "ogg"], key="music_upload")
        if music_file:
            music_dir = get_music_dir(selected_show)
            os.makedirs(music_dir, exist_ok=True)
            save_path = os.path.join(music_dir, music_file.name)
            with open(save_path, "wb") as f:
                f.write(music_file.read())
            st.success(f"Uploaded {music_file.name} to {music_dir}")

# --- Main Page: Producing Expander ---
if st.session_state.get("enable_producer") and selected_show:
    st.write("")
    with st.expander(f"Producing {selected_show}", expanded=False):
        media_dir = get_media_dir(selected_show)
        season_dirs = sorted([
            d for d in os.listdir(media_dir)
            if d.startswith("S") and os.path.isdir(os.path.join(media_dir, d))
        ])
        selected_season = st.selectbox(
            "Select Season",
            [s.replace("S", "") for s in season_dirs],
            key="producer_season_select"
        ) if season_dirs else None

        video_dir = os.path.join(media_dir, f"S{selected_season}") if selected_season else None

        # Find all clips in all episodes of the season
        clips = []
        episodes = []
        if video_dir and os.path.exists(video_dir):
            episodes = sorted([
                d for d in os.listdir(video_dir)
                if d.startswith("E") and os.path.isdir(os.path.join(video_dir, d))
            ])
            for ep in episodes:
                ep_dir = os.path.join(video_dir, ep)
                for ext in ("*.mp4", "*.mov", "*.webm", "*.avi", "*.mkv"):
                    clips += [
                        os.path.join(ep, os.path.basename(f))
                        for f in glob.glob(os.path.join(ep_dir, ext))
                    ]
        # Now we can build our two-column interface
        col1, col2 = st.columns([1, 1])

        with col1:
            if not clips:
                st.info("No video clips found in any episode of this season. Upload or create some first.")
            else:
                selected_clips = st.multiselect(
                    "Select video clips to edit (in order):", clips, key="select_clips"
                )
                st.divider()
                st.info("Video Options")
                #trim_start = st.number_input("Trim Start (sec)", min_value=0.0, max_value=3600.0, value=0.0, step=0.1, key="trim_start")
                #trim_end = st.number_input("Trim End (sec)", min_value=0.0, max_value=3600.0, value=0.0, step=0.1, key="trim_end")
                audio_vol = st.slider("Original Audio Volume", min_value=0.0, max_value=1.0, value=1.0, step=0.01, key="orig_audio_vol")
                remove_audio = st.checkbox("Remove Original Audio", key="remove_audio")
                st.divider()
                st.info("Overlays and Music")
                logo_dir = get_logo_dir(selected_show)
                logo_files = [f for f in os.listdir(logo_dir) if f.lower().endswith((".png",".jpg",".jpeg",".webp"))] if os.path.exists(logo_dir) else []
                overlay_img = st.selectbox("Image Overlay", ["None"] + logo_files, key="overlay_image")
                if overlay_img and overlay_img != "None":
                    preview = st.checkbox("Preview Image", key="preview_overlay_img")
                    if preview:
                        img_path = os.path.join(logo_dir, overlay_img)
                        st.image(img_path, caption="Preview: Overlay Image", use_container_width=True)
                overlay_x = st.slider("Overlay X Position (%)", 0, 100, 50, key="overlay_x")
                overlay_y = st.slider("Overlay Y Position (%)", 0, 100, 50, key="overlay_y")
                overlay_opacity = st.slider("Overlay Opacity", 0.0, 1.0, 1.0, 0.01, key="overlay_opacity")
                overlay_scale = st.slider("Overlay Scale", 0.1, 2.0, 1.0, 0.01, key="overlay_scale")
                # Music controls
                music_dir = get_music_dir(selected_show)
                music_files = [f for f in os.listdir(music_dir) if f.lower().endswith((".mp3",".wav",".ogg"))] if os.path.exists(music_dir) else []
                bg_music = st.selectbox("Background Music", ["None"] + music_files, key="bg_music")
                music_vol = st.slider("Music Volume", 0.0, 1.0, 1.0, key="music_vol")
                
                if st.button("Produce Video", key="produce_btn"):
                    try:
                        video_clips = []
                        for clip_name in selected_clips:
                            ep, fname = clip_name.split(os.sep)
                            clip_path = os.path.join(video_dir, ep, fname)
                            clip = VideoFileClip(clip_path)
                            st.write(f"Loaded {clip_path} ({clip.duration} seconds)")

                            if clip.duration <= 0.05:
                                st.error(f"Clip {clip_path} is zero or nearly zero seconds, skipping.")
                                continue
                            
                            # Audio controls
                            if remove_audio:
                                clip = clip.without_audio()
                            elif clip.audio is not None:
                                clip = clip.set_audio(clip.audio.fx(volumex, audio_vol))

                            video_clips.append(clip)

                        if not video_clips:
                            st.error("No valid clips to process. Aborting.")
                        else:
                            final_clip = concatenate_videoclips(video_clips, method="compose")
                            st.write("Concatenated video duration:", final_clip.duration)

                            # Overlay image
                            if overlay_img and overlay_img != "None":
                                img_path = os.path.join(logo_dir, overlay_img)
                                overlay = (
                                    ImageClip(img_path)
                                    .set_duration(final_clip.duration)
                                    .fx(resize, overlay_scale)
                                    .set_opacity(overlay_opacity)
                                    .set_position((
                                        int(final_clip.w * (overlay_x / 100.0)),
                                        int(final_clip.h * (overlay_y / 100.0))
                                    ))
                                )
                                final_clip = CompositeVideoClip([final_clip, overlay])

                            # Background music
                            if bg_music and bg_music != "None":
                                music_path = os.path.join(music_dir, bg_music)
                                if not os.path.exists(music_path):
                                    st.error(f"Music file {bg_music} not found at {music_path}")
                                    raise FileNotFoundError(f"Music file {bg_music} not found")
                                music_clip = AudioFileClip(music_path).fx(volumex, music_vol)
                                final_audio = music_clip.set_duration(final_clip.duration)
                                final_clip = final_clip.set_audio(final_audio)

                            st.write("Final video duration (before export):", final_clip.duration)
                            if final_clip.duration == 0:
                                st.error("Final video is zero seconds. Something went wrong.")
                            else:
                                out_dir = get_production_dir(selected_show)
                                os.makedirs(out_dir, exist_ok=True)
                                output_path = os.path.join(out_dir, f"{selected_show}_produced.mp4")
                                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                                final_clip.close()
                                for c in video_clips:
                                    c.close()
                                if bg_music and bg_music != "None":
                                    music_clip.close()
                                    final_audio.close()
                                st.success(f"Produced video saved: {output_path}")
                                st.session_state["last_produced_path"] = output_path

                    except Exception as e:
                        st.error(f"Error during video production: {e}")



        with col2:
            st.markdown("#### Video Player")
            # List all available videos in the selected season/episodes/production folder
            available_videos = []
            if video_dir and os.path.exists(video_dir):
                for ep in episodes:
                    ep_dir = os.path.join(video_dir, ep)
                    for ext in ("*.mp4", "*.mov", "*.webm", "*.avi", "*.mkv"):
                        available_videos += glob.glob(os.path.join(ep_dir, ext))
            # Also show produced videos
            prod_dir = get_production_dir(selected_show)
            if os.path.exists(prod_dir):
                available_videos += glob.glob(os.path.join(prod_dir, "*.mp4"))
            # Remove duplicates, just keep basenames for display
            display_names = [os.path.relpath(f, start=media_dir) if prod_dir not in f else f"PROD/{os.path.basename(f)}" for f in available_videos]
            video_dict = dict(zip(display_names, available_videos))
            if video_dict:
                play_video = st.selectbox("Select video to play", list(video_dict.keys()), key="play_video_selector")
                st.video(video_dict[play_video])
            else:
                st.info("No video files found. Add or create videos to play here.")


# --- YouTube Automation Sidebar (unchanged) ---
with st.sidebar.expander("YouTube Channel Automation", expanded=False):
    st.image("res/YT_sidebar.png")
    yt_show_list = list(st.session_state["shows"].keys())
    yt_show_choices = yt_show_list if yt_show_list else ["No Shows"]
    yt_selected_show = st.selectbox("YouTube: Select Show", yt_show_choices, key="yt_show_select")
    yt_selected_season = st.number_input("YouTube: Season", 1, 99, 1, key="yt_season")
    yt_selected_episode = st.number_input("YouTube: Episode", 1, 999, 1, key="yt_episode")
    st.button("Upload Episode to YouTube", key="yt_upload_button")
    st.button("Show Uploaded Episodes", key="yt_show_gallery")
    st.caption("Select a show, season, and episode, then upload it to your channel and organized playlist. Every episode is organized automatically into playlists matching your show titles.")

# --- MAIN PAGE LOGIC ---
# -- Main: Binge Gallery (not inside any expander) --
# --- Main: Binge Gallery (robust, works even if show missing from shows.json) ---
# --- Main Page: Write Episode Expander ---
write_ep_checked = st.session_state.get("write_episode_enable")
show = st.session_state.get("write_show_select")
season = st.session_state.get("write_season_select") or st.session_state.get("write_season_input")
episode = st.session_state.get("write_episode_select") or st.session_state.get("write_episode_input")

if write_ep_checked and show and season and episode:
    with st.expander("📝 Write Episode Script", expanded=True):
        meta_path = os.path.join(get_shows_dir(), show, "metadata.json")
        show_data = {}
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                show_data = json.load(f)
        cast = show_data.get("cast", [])
        behaviors = show_data.get("behaviors", {})
        drama = show_data.get("char_drama", {})
        fashion = show_data.get("fashion", {})

        st.markdown("#### Character Changes This Episode")
        char_controls = {}
        for char in cast:
            st.markdown(f"**{char}**")
            mood = st.selectbox(
                f"Mood for {char}",
                ["Neutral", "Happy", "Angry", "Sad", "Scheming", "Wild", "Paranoid", "Romantic"],
                key=f"main_mood_{char}"
            )
            char_drama = st.slider(
                f"Drama for {char}", 1, 10, drama.get(char, 5), key=f"main_drama_{char}_write"
            )
            char_fashion = st.text_input(
                f"Fashion update for {char}",
                fashion.get(char, ""), key=f"main_fashion_{char}_write"
            )
            happened = st.text_area(
                f"What happened to {char}?", "", key=f"main_happened_{char}_write"
            )
            char_controls[char] = {
                "mood": mood,
                "drama": char_drama,
                "fashion": char_fashion,
                "happened": happened,
            }

        st.markdown("#### Episode Context & Notes")
        # Select previous episodes as context
        transcripts_dir = get_transcripts_dir(show)
        season_dir = os.path.join(transcripts_dir, f"S{season}")
        prev_eps = sorted([
            d for d in os.listdir(season_dir)
            if d.startswith("E") and os.path.isdir(os.path.join(season_dir, d))
        ])
        context_episodes = st.multiselect(
            "Add previous episodes as context",
            prev_eps,
            default=prev_eps[:-1] if len(prev_eps) > 1 else []
        )
        episode_context = ""
        for ep in context_episodes:
            ep_dir = os.path.join(season_dir, ep)
            scene_files = sorted([
                f for f in os.listdir(ep_dir)
                if f.startswith("scene_") and f.endswith(".txt")
            ], key=lambda x: int(x.split("_")[-1].split(".")[0]))
            for f in scene_files:
                with open(os.path.join(ep_dir, f), "r", encoding="utf-8") as sf:
                    episode_context += sf.read() + "\n---\n"

        your_context = st.text_area("Write your own summary/context for this episode", key="main_your_context_write")

        if st.button("Create Script", key="main_write_create_script_btn"):
            script_parts = []
            script_parts.append(f"Show: {show}, Season {season}, Episode {episode}\n")
            script_parts.append("Character States/Events:\n")
            for char, changes in char_controls.items():
                script_parts.append(
                    f"{char}: Mood={changes['mood']}, Drama={changes['drama']}, Fashion={changes['fashion']}, Events={changes['happened']}"
                )
            script_parts.append("\n--- Context Episodes ---\n")
            script_parts.append(episode_context)
            script_parts.append("\n--- Your Notes ---\n")
            script_parts.append(your_context)
            script_text = "\n".join(script_parts)
            ep_dir = os.path.join(season_dir, f"E{episode}")
            os.makedirs(ep_dir, exist_ok=True)
            scene_path = os.path.join(ep_dir, "scene_0.txt")
            with open(scene_path, "w", encoding="utf-8") as f:
                f.write(script_text)
            st.success(f"Episode script saved: {scene_path}")

if "binge_gallery" in st.session_state:
    show, season = st.session_state["binge_gallery"]
    show_dir = os.path.join("data/media/show_videos", show, f"S{season}")
    meta_path = os.path.join(get_shows_dir(), show, "metadata.json")
    logo_path = None
    for ext in ("png", "jpg", "jpeg", "webp"):
        candidate = os.path.join("data/media/show_logos", f"{show}.{ext}")
        if os.path.exists(candidate):
            logo_path = candidate
            break
    music_prompt_path = os.path.join(get_music_dir(show), "show_music_prompt.txt")
    music_files = []
    music_dir = os.path.join("data", "media", "show_music", show)
    if os.path.exists(music_dir):
        music_files = [f for f in os.listdir(music_dir) if f.endswith((".mp3", ".wav", ".ogg"))]
    # Gracefully handle missing metadata
    meta = {}
    meta_found = False
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as mf:
            meta = json.load(mf)
            meta_found = True

    # Find episodes
    episodes = sorted([d for d in os.listdir(show_dir) if d.startswith("E") and os.path.isdir(os.path.join(show_dir, d))]) if os.path.exists(show_dir) else []

    with st.expander(f"{show} – Season {season} Gallery", expanded=False):
        col1, col2, col3= st.columns([2, 1, 2], gap="medium")

        with col1:
            # Theme song (audio)
            music_dir = os.path.join("data", "media", "show_music", show)
            music_files = [f for f in os.listdir(music_dir) if f.endswith((".mp3", ".wav", ".ogg"))] if os.path.exists(music_dir) else []
            if music_files:
                st.markdown("#### Theme Song")
                for mfile in music_files:
                    mpath = os.path.join(music_dir, mfile)
                    st.audio(mpath)
                    with open(mpath, "rb") as mf:
                        st.download_button(
                            "Download Theme Song",
                            mf,
                            file_name=os.path.basename(mpath),
                            mime="audio/mpeg",
                            key=f"dl_musicfile_{show}_{mfile}"
                        )
            else:
                st.info("No theme song found for this show.")
        with col2:
            pass
        with col3:
            # --- Show Logo image at the top, large and centered ---
            
            logo_path = os.path.join("data", "media", "show_logos", f"{show}_logo.png")
            if os.path.exists(logo_path):
                st.image(logo_path, width=350, caption=None)  # Or with caption, your choice

            # Metadata, formatted and readable
            #theme = meta.get('theme', '[No theme]')
            #style = meta.get('style', '[No style]')
            #cast = ', '.join(meta.get('cast', [])) if meta.get('cast') else '[No cast listed]'
            #drama = meta.get('drama', '[No drama level]')
            #desc = meta.get('desc', '[No description]')
            #st.markdown(f"<b>Theme:</b> {theme}<br>"
            #            f"<b>Style:</b> {style}<br>"
            #            f"<b>Cast:</b> {cast}<br>"
            #            f"<b>Drama Level:</b> {drama}<br>"
            #            f"<b>Description:</b> {desc}", unsafe_allow_html=True)
            #if not meta_found:
            #    st.warning(f"Metadata for '{show}' is missing. Add this show in Show Tools for full features.")

        # --- Episodes/videos (always display) ---
        st.markdown("#### Episodes")
        if episodes:
            for ep in episodes:
                ep_dir = os.path.join(show_dir, ep)
                video_files = [f for f in os.listdir(ep_dir) if f.endswith((".mp4", ".webm", ".mov", ".avi"))]
                if video_files:
                    vcols = st.columns(len(video_files))
                    for idx, v in enumerate(video_files):
                        with vcols[idx]:
                            vid_path = os.path.join(ep_dir, v)
                            st.video(vid_path)
                            st.caption(v)
                            with open(vid_path, "rb") as vf:
                                st.download_button(
                                    "Download Video",
                                    vf,
                                    file_name=os.path.basename(vid_path),
                                    mime="video/mp4",
                                    key=f"dl_vid_{show}_{season}_{ep}_{idx}",
                                )
                else:
                    st.info(f"No videos found for episode {ep.replace('E','')}.")
        else:
            st.info("No episodes found for this season.")


# -- Show Tools Display (on main page, not inside expander if checkbox is off) --
if "show_tools_display" in st.session_state and st.session_state["show_tools_display"].get("enabled"):
    disp = st.session_state["show_tools_display"]
    if disp["scenes"] or disp["prompts"] or disp["music"]:
        with st.expander("Show Prompts, Transcripts, and Music", expanded=False):
            rows = []
            for fname in disp["scenes"]:
                path = os.path.join(
                    get_transcripts_dir(disp["show"]),
                    disp["season"], disp["episode"], fname
                )
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    rows.append({"Type": "Scene Transcript", "Name": fname, "Content": content})
            for fname in disp["prompts"]:
                path = os.path.join(get_prompts_dir(disp["show"]), fname)
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    rows.append({"Type": "Prompt", "Name": fname, "Content": content})
            for fname in disp["music"]:
                path = os.path.join(get_music_dir(disp["show"]), fname)
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    rows.append({"Type": "Music Prompt", "Name": fname, "Content": content})
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("No scenes, prompts, or music selected to display.")

# -- Create New Show (main area, only if enabled from Show Tools) --
if enable_new_show:
    #with st.expander("Create a New Show – Pick a Genre and optional Show Style", expanded=True):
        # Always use a key prefix to avoid duplicate keys
        theme_selector.theme_grid(st.session_state, enable_new_show, key_prefix="newshow_")

        if "new_show" in st.session_state:
            st.success(f"Show '{st.session_state['new_show']}' created!")

else:
    valid_for_builder = (
        selected_show_bw
        and selected_show_bw not in ("No Shows", "Create New Show")
        and selected_season_bw
        and selected_season_bw not in ("None", "No Seasons")
        and selected_show_bw in st.session_state["shows"]
    )
    if valid_for_builder:
        st.title(f"{selected_show_bw} - S{selected_season_bw}")
        scene_engine.display_scene_builder(
            selected_show_bw, selected_season_bw, None, st.session_state
        )
    # Optionally show a helpful message when nothing is valid
    else:
        pass
save_json(st.session_state["shows"], SHOWS_FILE)

