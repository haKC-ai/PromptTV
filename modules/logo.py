import streamlit as st
from api import openai_logo

def generate_logo(show):
    st.info("Generating logo...")
    img_bytes, logo_file = openai_logo.create_logo(show)
    if img_bytes:
        st.image(img_bytes, caption=f"Logo for {show}")
        st.success(f"Logo saved: {logo_file}")
    else:
        st.error("Logo generation failed.")
