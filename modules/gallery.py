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
    
def show_gallery(uploads):
    st.title("Uploaded Episodes")
    for show, seasons in uploads.items():
        st.header(show)
        for season, episodes in seasons.items():
            st.subheader(f"Season {season}")
            for episode, meta in episodes.items():
                st.markdown(f"- [Episode {episode}: {meta['title']}](https://youtu.be/{meta['video_id']})")