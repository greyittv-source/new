import os
import sys
import json
from datetime import datetime, timedelta

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1]

from upload_youtube import get_authenticated_service, upload_video
from upload_daily_videos import upload_video_public

def replace_shorts():
    youtube = get_authenticated_service()
    if not youtube:
        print("❌ 인증 실패.")
        return

    print("🔍 유튜브 채널에서 기존 쇼츠 영상을 검색하여 삭제합니다...")
    request = youtube.search().list(part="snippet", forMine=True, maxResults=50, type="video")
    response = request.execute()
    
    deleted_count = 0
    for item in response.get("items", []):
        if "snippet" not in item:
            continue
        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        if "#Shorts" in title:
            print(f"🗑️ 기존 쇼츠 삭제 중: {title} (ID: {video_id})")
            try:
                youtube.videos().delete(id=video_id).execute()
                print(f"✅ 삭제 완료")
                deleted_count += 1
            except Exception as e:
                print(f"❌ 삭제 실패: {e}")
                
    print(f"\n총 {deleted_count}개의 기존 쇼츠를 삭제했습니다.")

    metadata_path = os.path.join("daily_playlists", "daily_playlists_metadata.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    now = datetime.now().astimezone()
    
    for item in metadata_list:
        day_num = item["week"]
        title = item["youtube_title"]
        description = item["youtube_description"]
        tags = item["youtube_tags"]
        
        video_file = item["video_file"]
        if "daily_playlists" not in video_file:
            video_file = os.path.join("daily_playlists", video_file)
            
        theme_dir = os.path.dirname(video_file)
        shorts_file = os.path.join(theme_dir, f"shorts_day{day_num}.mp4")
        
        import re
        base_desc_no_ts = re.sub(r"\[Timestamps\].*", "", description, flags=re.DOTALL).strip()
        
        shorts_title = f"{title} #Shorts"
        if len(shorts_title) > 100:
            shorts_title = shorts_title[:95] + "..."
            
        shorts_description = f"{base_desc_no_ts}\n\n⚠️ 본 영상의 음악과 이미지는 모두 AI 기술을 활용하여 자동 생성(창작)되었습니다.\n(This video's music and images were created using AI technology.)\n\n#Shorts #Lofi #GreyitTV"
        shorts_tags = tags + ["Shorts", "Lofi"]

        if day_num == 1:
            print(f"\n=========================================")
            print(f"📦 [Week 1] 새 쇼츠 즉시 공개 업로드 개시")
            print(f"=========================================")
            if os.path.exists(shorts_file):
                upload_video_public(youtube, shorts_title, shorts_description, shorts_tags, shorts_file)
        else:
            print(f"\n=========================================")
            print(f"📦 [Week {day_num}] 새 쇼츠 핫타임(16:00) 예약 업로드 개시")
            print(f"=========================================")
            days_offset = day_num - 1
            shorts_time = (now + timedelta(days=days_offset)).replace(hour=16, minute=0, second=0, microsecond=0)
            
            if shorts_time < now + timedelta(minutes=15):
                shorts_time = now + timedelta(hours=1)
                
            shorts_iso = shorts_time.isoformat()
            
            if os.path.exists(shorts_file):
                upload_video(youtube, shorts_title, shorts_description, shorts_tags, shorts_file, publish_time=shorts_iso)

    print("\n🎉 모든 쇼츠 영상이 성공적으로 교체되었습니다!")

if __name__ == "__main__":
    replace_shorts()
