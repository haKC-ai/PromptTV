from googleapiclient.discovery import build

def get_or_create_playlist(creds, show_title):
    youtube = build("youtube", "v3", credentials=creds)
    # First, try to find existing playlist
    playlists = youtube.playlists().list(part="snippet", mine=True, maxResults=50).execute()
    for pl in playlists.get("items", []):
        if pl["snippet"]["title"] == show_title:
            return pl["id"]
    # Not found, create it
    response = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": show_title, "description": f"Playlist for {show_title}"},
            "status": {"privacyStatus": "public"}
        }
    ).execute()
    return response["id"]

def add_video_to_playlist(creds, playlist_id, video_id):
    youtube = build("youtube", "v3", credentials=creds)
    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id}
            }
        }
    ).execute()
