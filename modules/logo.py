import streamlit as st
from api import openai_logo
import os

def generate_logo(show):
    st.info("Generating logo...")
    logo_file = openai_logo.create_logo(show)
    st.image(logo_file)
    st.success(f"Logo saved: {logo_file}")
