import streamlit as st
from api import suno
import os

def generate_music(show):
    st.info("Generating theme music...")
    music_file = suno.create_theme_music(show)
    st.audio(music_file)
    st.success(f"Music saved: {music_file}")
