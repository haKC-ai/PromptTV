import streamlit as st
from api import veo  # <-- MOVE THIS TO THE TOP
from api import veo, openai_scene_writer
import os

def save_scene_to_file(show, season, episode, scene_num, text):
    dir_path = os.path.join(
        "data", "transcripts",
        str(show),
        f"S{season}",
        f"E{episode}"
    )
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"scene_{scene_num}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    return file_path

def get_scene_files(show, season, episode):
    dir_path = os.path.join(
        "data", "transcripts",
        str(show),
        f"S{season}",
        f"E{episode}"
    )
    if not os.path.exists(dir_path):
        return []
    files = sorted([
        os.path.join(dir_path, fname)
        for fname in os.listdir(dir_path)
        if fname.startswith("scene_") and fname.endswith(".txt")
    ], key=lambda x: int(x.split("_")[-1].split(".")[0]))
    return files

def display_scene_builder(show, season, episode, session_state):
    show_data = session_state["shows"][show]
    seasons = show_data.setdefault("seasons", {})
    episodes = seasons.setdefault(str(season), {})
    ep_data = episodes.setdefault(str(episode), {"scenes": [], "transcript": []})

    # Show last scene's prompt as code/caption (if any)
    if ep_data["scenes"]:
        with st.expander("Last Scene", expanded=False):
        
            st.caption(ep_data["scenes"][-1]["prompt"])

    col0, col1, col2, col3 = st.columns([2, 2, 2, 2])

    # Transcript (from all files)
    with col0:
        st.subheader("Transcript")
        scene_files = get_scene_files(show, season, episode)
        transcript_texts = []
        for idx, path in enumerate(scene_files):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                transcript_texts.append(f"Scene {idx}: {content}")
        transcript_panel = "\n\n".join(transcript_texts) if transcript_texts else "No transcript yet."
        st.markdown(
            f"<div style='height:420px; overflow-y:scroll; background:#1a1a1a; color:#f6f6f6; border-radius:8px; padding:10px; font-size:0.93em;'>{transcript_panel.replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True
        )

    # Scene Composer
    with col1:
        st.header("Scene Composer")
        st.write(f"Show: {show_data['name']} | Season: {season} | Episode: {episode}")
        if ep_data["scenes"]:
            st.video(ep_data["scenes"][-1]["video_path"])
        else:
            # Build a summary of all scenes so far this season (text only)
            season_transcripts = []
            for ep_num, episode_obj in sorted(seasons.items(), key=lambda x: int(x[0])):
                if episode_obj.get("transcript"):
                    for i, scene in enumerate(episode_obj["transcript"], 1):
                        season_transcripts.append(f"Episode {ep_num}, Scene {i}: {scene}")
            if season_transcripts:
                st.markdown("#### What’s happened so far this season:")
                st.markdown("<br>".join(season_transcripts), unsafe_allow_html=True)
            else:
                st.info("Nothing yet this season.")

    # Compose Next Scene (with context selection)
    with col2:
        st.subheader("Compose Next Scene")
        scene_prompt = st.text_area("Describe what happens next (leave blank to randomize)", "")
        # Multi-select prior scenes as context
        scene_options = []
        for idx, path in enumerate(scene_files):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            scene_options.append(f"Scene {idx}: {content[:60].replace(chr(10),' ')}...")
        selected_contexts = st.multiselect(
            "Select previous scenes as context",
            scene_options,
            default=scene_options[-3:] if len(scene_options) >= 3 else scene_options
        )
        # Get actual scene texts for prompt
        context_texts = []
        for label in selected_contexts:
            idx = int(label.split(":")[0].split()[-1])
            with open(scene_files[idx], "r", encoding="utf-8") as f:
                context_texts.append(f.read())
        context_text = "\n\n".join(context_texts)

    # Character selection/events
    with col3:
        st.subheader("Choose active characters")
        display_choices = []
        display_map = {}
        for char in show_data["cast"]:
            traits = show_data.get("behaviors", {}).get(char, [])
            traits_label = f" ({', '.join(traits)})" if traits else ""
            display = f"{char}{traits_label}"
            display_choices.append(display)
            display_map[display] = char

        selected_display = st.multiselect(
            "Active characters",
            display_choices,
            default=display_choices
        )

        # Map back to raw character names for downstream code
        character_choices = [display_map[disp] for disp in selected_display]
        funny_options = [
            "Nothing special",
            "Got pregnant",
            "Died (maybe?)",
            "Got super drunk",
            "Started a fight",
            "Had a secret affair",
            "Became a meme",
            "Was exposed on social media",
            "Joined a cult",
            "Won the lottery",
            "Lost their pants",
            "Enter your own..."
        ]
        character_events = {}
        for character in character_choices:
            event = st.multiselect(
                f"What happened to {character}?",
                funny_options,
                key=f"{character}_event"
            )
            if "Enter your own..." in event:
                custom = st.text_input(f"Enter custom event for {character}:", key=f"{character}_custom_event")
                event = [e for e in event if e != "Enter your own..."]
                if custom:
                    event.append(custom)
            character_events[character] = event

    # Build character events fragment for AI prompt
    event_lines = []
    for char, events in character_events.items():
        if not events:
            continue
        if not isinstance(events, list):
            events = [events]
        filtered = [e for e in events if e and e.lower() != "nothing special"]
        if filtered:
            event_lines.append(f"{char}: {', '.join(filtered)}")
    events_fragment = " | ".join(event_lines)
    events_text = f"Character events this scene: {events_fragment}." if events_fragment else ""

    # Build full OpenAI scene prompt
    show_context = (
        f"Show Title: {show_data['name']}\n"
        f"Season: {season}, Episode: {episode}\n"
        f"Cast: {', '.join(show_data['cast'])}\n"
        f"Behavioral Traits: {', '.join(show_data.get('behaviors', []))}\n"
        f"Drama Level: {show_data.get('drama', 5)}\n"
        f"Context scenes:\n{context_text}\n"
        f"Active Characters: {', '.join(character_choices)}\n"
        f"{events_text}\n"
        f"Next scene idea: {scene_prompt if scene_prompt else 'Random or AI-generated'}\n"
        "Write a highly descriptive, vivid, and TV-ready next scene that fits the story, the character traits, and keeps perfect narrative continuity."
    )

    if st.button("Generate Scene"):
        ai_scene = openai_scene_writer.compose_scene(show_context)
        prompt = ai_scene if ai_scene else scene_prompt or veo.random_scene_prompt(show_data, character_choices)
        video_path = veo.generate_scene(prompt, show, season, episode)
        new_scene = {"prompt": prompt, "video_path": video_path}
        ep_data["scenes"].append(new_scene)
        ep_data["transcript"].append(prompt)
        # Save to dedicated file for this scene
        scene_num = len(ep_data["scenes"]) - 1
        save_scene_to_file(show, season, episode, scene_num, prompt)
        st.success("Scene generated!")
        st.rerun()

    if st.button("End Show"):
        veo.create_intro_and_transitions(show, season, episode)
        st.success("Show completed. Intro and transitions generated.")

    # Veo: Send any scene for video generation (sidebar, or here at bottom)

