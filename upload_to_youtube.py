"""
YouTube Upload Script - Lingexa Idioms
"""

import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

CHANNEL_NAME = "Lingexa Idioms"

def get_authenticated_service():
    client_id = (os.getenv('YOUTUBE_CLIENT_ID') or os.getenv('YT_CLIENT_ID', '')).strip()
    client_secret = (os.getenv('YOUTUBE_CLIENT_SECRET') or os.getenv('YT_CLIENT_SECRET', '')).strip()
    refresh_token = (os.getenv('YOUTUBE_REFRESH_TOKEN') or os.getenv('YT_REFRESH_TOKEN', '')).strip()
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing YouTube credentials!")
    creds = Credentials(None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token", client_id=client_id, client_secret=client_secret, scopes=["https://www.googleapis.com/auth/youtube"])
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def generate_video_metadata(words_data, reel_data=None):
    if not words_data:
        return f"English Idioms - {CHANNEL_NAME}", f"Master English idioms with {CHANNEL_NAME}!", ["english idioms", "learn english", CHANNEL_NAME.replace(' ', '')]
    first_words = [w.get("word", "") for w in words_data[:3]]
    words_count = len(words_data)
    title = f"Learn {words_count} English Idioms - {', '.join(first_words)} | Meaning & Origin"
    lines = [f"🎯 Master {words_count} English idioms with {CHANNEL_NAME}!", f"", f"=== TODAY'S IDIOMS ===", f""]
    for i, w in enumerate(words_data, 1):
        word = w.get("word", "")
        definition = w.get("definition", "")
        example = w.get("example", "")
        origin = w.get("origin", "")
        fun_fact = w.get("fun_fact", "")
        lines.append(f"{i}. {word}")
        lines.append(f"   Meaning: {definition}")
        lines.append(f"   Example: {example}")
        if origin:
            lines.append(f"   Origin: {origin}")
        if fun_fact:
            lines.append(f"   💡 {fun_fact}")
        lines.append(f"")
    lines.extend([f"=== ABOUT {CHANNEL_NAME.upper()} ===", f"", f"Master English idioms every day!", f"🔔 Subscribe for daily lessons!", f"", f"=== HASHTAGS ===", f"#LingexaIdioms #EnglishIdioms #LearnEnglish #EnglishExpressions #ESL #EnglishVocabulary #Idioms #LanguageLearning #Shorts"])
    return title, "\n".join(lines), ["english idioms", "learn english", "idioms and phrases", "english expressions", "idiom meanings", "esl", "english vocabulary", CHANNEL_NAME.replace(' ', '').lower()] + [w.get("word", "").lower() for w in words_data[:5]]

def upload_to_youtube(video_path, title, description, tags=None, category_id='27'):
    if tags is None:
        tags = ['english idioms', 'learn english', CHANNEL_NAME.replace(' ', '').lower()]
    youtube = get_authenticated_service()
    body = {'snippet': {'title': title, 'description': description, 'tags': tags, 'categoryId': category_id}, 'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}}
    media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
    video_id = response.get('id')
    print(f"[youtube] Uploaded! Video ID: {video_id}")
    return {"status": "success", "video_id": video_id, "title": title}
