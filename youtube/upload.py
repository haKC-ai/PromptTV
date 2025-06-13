from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video(creds, title, description, file_path):
    youtube = build("youtube", "v3", credentials=creds)
    media = MediaFileUpload(file_path, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "24"
            },
            "status": {
                "privacyStatus": "unlisted"
            }
        },
        media_body=media
    )
    response = request.execute()
    return response["id"]
