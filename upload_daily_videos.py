import os
import sys
import json
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1]

from upload_youtube import get_authenticated_service, upload_video

def upload_video_public(youtube, title, description, tags, file_path):
    from googleapiclient.http import MediaFileUpload
    print(f"\n🎬 유튜브 업로드 시작...\n - 제목: {title}\n - 업로드 상태: 즉시 공개 (Public)\n - 파일: {file_path}")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '10'  # Music
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
            'containsSyntheticMedia': True
        }
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    print("⏳ 동영상을 유튜브 서버로 전송 중입니다...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"진행률: {int(status.progress() * 100)}%")
            
    print(f"✅ 성공! 비디오 업로드 완료 (공개 상태)")
    print(f"🔗 확인 링크: https://studio.youtube.com/video/{response['id']}/edit")
    return response['id']

def run_daily_uploads():
    print("🚀 [콘텐츠 팩토리] 5일 치 예약 콘텐츠 자동 업로드 파이프라인 가동\n")
    youtube = get_authenticated_service()
    if not youtube:
        print("❌ 인증 실패.")
        return

    metadata_path = os.path.join("daily_playlists", "daily_playlists_metadata.json")
    if not os.path.exists(metadata_path):
        print("❌ 메타데이터 파일이 존재하지 않습니다.")
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    now = datetime.now().astimezone()
    
    for item in metadata_list:
        day_num = item["week"]
        title = item["youtube_title"]
        description = item["youtube_description"]
        tags = item["youtube_tags"]
        
        # 롱폼 경로
        video_file = os.path.join("daily_playlists", item["video_file"].split("\\")[-1])
        if "daily_playlists" in item["video_file"]:
            video_file = item["video_file"]
            
        # 쇼츠 경로 추론
        theme_dir = os.path.dirname(video_file)
        shorts_file = os.path.join(theme_dir, f"shorts_day{day_num}.mp4")
        
        # 쇼츠용 설명: 타임스탬프 제거
        import re
        base_desc_no_ts = re.sub(r"\[Timestamps\].*", "", description, flags=re.DOTALL).strip()
        
        shorts_title = f"{title} #Shorts"
        # 타이틀 100자 제한
        if len(shorts_title) > 100:
            shorts_title = shorts_title[:95] + "..."
            
        shorts_description = f"{base_desc_no_ts}\n\n#Shorts #Lofi #GreyitTV"
        
        # 롱폼 설명 5000자 제한
        if len(description) > 4900:
            description = description[:4900] + "\n..."
            
        shorts_tags = tags + ["Shorts", "Lofi"]

        if day_num == 1:
            print(f"=========================================")
            print(f"📦 [Week {day_num}] 즉시 공개(Public) 업로드 개시")
            print(f"=========================================")
            if os.path.exists(shorts_file):
                upload_video_public(youtube, shorts_title, shorts_description, shorts_tags, shorts_file)
            if os.path.exists(video_file):
                upload_video_public(youtube, title, description, tags, video_file)
        else:
            print(f"=========================================")
            print(f"📦 [Week {day_num}] 핫타임(18:00) 예약 업로드 개시")
            print(f"=========================================")
            # Week 2는 내일(+1일), Week 3는 모레(+2일) ...
            days_offset = day_num - 1
            
            # 쇼츠는 16시에 예약 (롱폼 전 예고편)
            shorts_time = (now + timedelta(days=days_offset)).replace(hour=16, minute=0, second=0, microsecond=0)
            # 롱폼은 18시에 예약
            longform_time = (now + timedelta(days=days_offset)).replace(hour=18, minute=0, second=0, microsecond=0)
            
            # YouTube API 요구사항: 예약 시간은 현재 시간으로부터 최소 15분 이후여야 함
            # 과거 시간일 경우 처리 로직 방어 (만약 스크립트를 밤에 돌려서 내일 18시가 무조건 미래겠지만 안전장치)
            if shorts_time < now + timedelta(minutes=15):
                shorts_time = now + timedelta(hours=1)
            if longform_time < shorts_time + timedelta(minutes=15):
                longform_time = shorts_time + timedelta(hours=1)
                
            shorts_iso = shorts_time.isoformat()
            longform_iso = longform_time.isoformat()
            
            if os.path.exists(shorts_file):
                upload_video(youtube, shorts_title, shorts_description, shorts_tags, shorts_file, publish_time=shorts_iso)
            if os.path.exists(video_file):
                upload_video(youtube, title, description, tags, video_file, publish_time=longform_iso)

    print("\n🎉 모든 파이프라인 업로드가 성공적으로 완료되었습니다!")

if __name__ == "__main__":
    run_daily_uploads()
