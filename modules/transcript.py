import streamlit as st
import os

DATA_DIR = "data"

def save_transcript(show, season, episode):
    transcript_path = os.path.join(DATA_DIR, "transcripts", f"{show}_S{season}E{episode}.txt")
    shows = st.session_state["shows"]
    scenes = shows[show]["seasons"][str(season)][str(episode)]["transcript"]
    with open(transcript_path, "w") as f:
        for line in scenes:
            f.write(line + "\n")
    st.success(f"Transcript saved to {transcript_path}")
