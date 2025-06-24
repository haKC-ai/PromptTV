# PromptTV

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built_with-Streamlit-ff4b4b)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-Beta-yellow)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)]()
![prompTV_streamlit_Banner23](https://github.com/user-attachments/assets/e08f328c-7282-446e-afe1-f66255c2cc6c)

### PromptTV is a full-stack production studio interface to fully automate a final video from a simple idea prompt. 

<p align="center">
  <img src="https://raw.githubusercontent.com/haKC-ai/PromptTV/refs/heads/main/res/Screenshot_2025-06-24-08-55-57-42_965bbf4d18d205f782c6b8409c5773a4.jpg" alt="PromptTV Screenshot" width="600">
</p>

- Check the output from from this here:  https://youtu.be/SrG25lr5VOM?si=BLc_aQoed3fvAIBy 

- If you've had an idea for a TV show, bring it to life.
Git the code here: https://github.com/haKC-ai/PromptTV

- Enables a prompt-driven, AI-generated streaming content pipeline

`Supports creation of:`
- Full season, Episode and Scene support
- Character Transcripts (automated, or full control)
- Logos
- Music
- Video prompts
- Custom voices
- Full character builder with drama level, physical traits, and behaviors

- Provides scene-to-scene event control
- Allows design of dynamic, endlessly branching shows
- Functions as an interactive TV show studio
- Integrates audience input through Twitter hashtag monitoring
- Combines AI and automation to drive content generation
- Supports automated upload to YouTube

# Features

- AI-generated show creation and scripting
- Multi-genre and spicy show picker (spicy shows highlighted)
- On-demand logo and music generation
- Upload episodes to YouTube with playlist management
- Audience Twitter integration for show ideas
- Media and transcript gallery
![Screenshot 2025-06-13 at 1 04 41 PM](https://github.com/user-attachments/assets/d1a209f8-4c15-499b-8e71-4d73ac86bf06)


# PromptTV App Overview

## Data Structure Initialization
- Ensures required directories exist:
  - data/
  - data/shows/
  - data/transcripts/
  - data/media/show_videos/
  - data/media/show_logos/
  - data/media/show_music/
- Initializes or loads:
  - shows.json to track available shows
  - uploads.json to track uploaded content
  - Both are stored in session state

## Path Utility Functions
- Defines reusable functions to retrieve:
  - Show directory
  - Transcript directory
  - Prompt directory
  - Music directory

## BingeWatch Viewer
- Sidebar interface to:
  - Select available shows and seasons
  - Browse and display galleries of episodes
  - Handles missing or empty folders gracefully

## Logo Generator
- Generates AI-based logos for selected shows
- Uses OpenAI API to create 1024x1024 transparent logos
- Metadata-driven styling using theme, style, and description
- Supports download and re-use of previously generated logos

## Writer Interface
- Allows user to:
  - Select or manually enter season and episode
  - Prepare for transcript and scriptwriting tasks

## Show Tools
- Provides tools per show:
  - Launch media gallery
  - Regenerate show logo
  - Placeholder button for show intro
  - Generate a music prompt based on show metadata
  - Optionally save prompt or send it to a music service (Suno)
  - View existing scene files, prompt text, and music drafts

## Veo Integration for Video Creation
- UI to:
  - Select show, season, episode, and scene
  - Choose additional context scenes
  - Load show metadata for enhanced prompt generation
  - Generate video prompt text with option to send to Veo
  - Supports just saving the prompt locally

## Library and Module Usage
- Uses moviepy for video and audio editing workflows
- Loads OpenAI API key from a .env file
- Includes custom modules:
  - theme_selector, scene_engine, music, logo, transcript
  - youtube integrations for upload and playlist creation
  - veo API for video generation


# Setup

Clone the repo, run the installer, and launch the app:

git clone https://github.com/yourusername/PromptTV.git
cd PromptTV
bash installer.sh

Open http://localhost:2323 in your browser.

# How to Use

1. Launch the app by running bash installer.sh. The Streamlit server starts on port 2323.
2. Open your browser to http://localhost:2323
3. Use the sidebar to create a new show or select an existing show.
4. Pick genres and styles (spicy shows are highlighted)
5. Name your show, choose drama level, and describe cast and behaviors.
6. Write or randomize scenes for your episodes.
7. Generate show logos and theme music.
8. Accept or reject scene ideas submitted via Twitter hashtag (see Twitter integration documentation).
9. Review galleries of all your videos, music, and logos.
10. Upload finished episodes directly to YouTube, grouped by show, season, and episode.

# Directory Structure
```
.
├── api/
├── app.py
├── data/
├── modules/
├── res/
├── twitter/
├── youtube/
├── requirements.txt
├── installer.sh
├── scaffold_promptTV.sh
```
# License

MIT

# Contributing

Pull requests welcome. See CONTRIBUTING.md for guidelines.

# Credits

Brought to you by HAKC.AI

This README was generated by a script.
