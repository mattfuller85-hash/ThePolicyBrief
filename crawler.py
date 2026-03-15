import os
import json
from googleapiclient.discovery import build
from dotenv import load_dotenv

# The "Backwash" Effect:
# This script scans the official Policy Brief YouTube channel for newly uploaded videos.
# It extracts the Bill ID from the YouTube description (or title) and updates our local JSON
# so the Web Hub can automatically embed the video for that specific bill.

def get_youtube_service():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("❌ YOUTUBE_API_KEY is missing from .env")
        return None
    return build('youtube', 'v3', developerKey=api_key)

def fetch_recent_videos(youtube, channel_id: str, max_results: int = 10):
    """Fetch the latest videos from a specific YouTube channel."""
    # First, get the 'uploads' playlist ID for the channel
    print(f"Fetching channel info for: {channel_id}")
    channel_response = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    
    if not channel_response.get('items'):
        print(f"❌ Could not find channel {channel_id}")
        return []
        
    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Next, get the videos in the uploads playlist
    print(f"Fetching recent videos from playlist: {uploads_playlist_id}")
    playlist_response = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=max_results
    ).execute()
    
    video_data = []
    for item in playlist_response.get('items', []):
        snippet = item['snippet']
        video_data.append({
            'video_id': snippet['resourceId']['videoId'],
            'title': snippet['title'],
            'description': snippet['description'],
            'published_at': snippet['publishedAt'],
            'url': f"https://www.youtube.com/watch?v={snippet['resourceId']['videoId']}"
        })
        
    return video_data

def backwash_urls_to_web_hub(video_data: list, web_data_path: str = "web/src/data/audits.json"):
    """
    Search our local web data JSON for bills that match the YouTube videos.
    Update the local JSON with the YouTube URL.
    """
    if not os.path.exists(web_data_path):
        print(f"❌ Web data file not found at {web_data_path}")
        return
        
    with open(web_data_path, "r", encoding="utf-8") as f:
        audits = json.load(f)
        
    updated_count = 0
    
    for video in video_data:
        # Assuming the Bill ID is explicitly mentioned in the title or description (e.g., "HR551")
        # For a more robust mapping, we might search for exact regex patterns
        # For now, we do a basic substring match against all known bill IDs in our data
        
        for audit in audits:
            bill_id = audit.get("bill_id", "")
            if not bill_id:
                continue
                
            # If the video doesn't already have an embedded URL, and the bill ID is in the title/desc
            if not audit.get("youtube_url"):
                if bill_id.lower() in video["title"].lower() or bill_id.lower() in video["description"].lower():
                    print(f"🔄 Mapping Video [{video['title']}] -> Bill [{bill_id}]")
                    audit["youtube_url"] = video["url"]
                    updated_count += 1
                    
    if updated_count > 0:
        with open(web_data_path, "w", encoding="utf-8") as f:
            json.dump(audits, f, indent=2)
        print(f"✅ 'Backwash' Complete. Successfully mapped {updated_count} YouTube URLs.")
    else:
        print("ℹ️ No new videos mapped. Everything is up to date.")

def run_crawler():
    load_dotenv()
    youtube = get_youtube_service()
    if not youtube:
        return
        
    # The user's YouTube Channel ID
    # Note: We will need the actual channel ID from the user eventually.
    # We can default to an environment variable.
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    if not channel_id:
        print("❌ YOUTUBE_CHANNEL_ID is missing from .env")
        return
        
    videos = fetch_recent_videos(youtube, channel_id=channel_id)
    if videos:
        backwash_urls_to_web_hub(videos)

if __name__ == "__main__":
    run_crawler()
