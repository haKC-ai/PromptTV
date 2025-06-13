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
