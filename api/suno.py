import os

def create_theme_music(show):
    music_file = f"data/media/show_music/{show}_theme.mp3"
    open(music_file, "a").close()
    return music_file
