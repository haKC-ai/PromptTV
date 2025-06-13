import os

def create_logo(show):
    logo_file = f"data/media/show_logos/{show}_logo.png"
    open(logo_file, "a").close()
    return logo_file
