from youtube_transcript_api import YouTubeTranscriptApi
import json
import urllib.request
import re

video_id = "zvnbF9-Y_4w"

try:
    # Get Title from YouTube page
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    title_match = re.search(r'<title>(.*?)</title>', html)
    title = title_match.group(1) if title_match else "Unknown Title"
    print(f"Title: {title}")

    # Get Transcript
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
    text = " ".join([t['text'] for t in transcript])
    print("\n--- Transcript ---")
    print(text)
except Exception as e:
    print(f"Error: {e}")
