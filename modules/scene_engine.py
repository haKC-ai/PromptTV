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
