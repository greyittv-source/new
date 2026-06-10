import os
import sys
import json
from upload_youtube import get_authenticated_service, upload_video

sys.stdout.reconfigure(encoding='utf-8')

def upload_longform():
    print("==================================================")
    print("🎬 [Greyit TV] Day 1 롱폼(1시간 믹스) 유튜브 업로드 시작")
    print("==================================================")
    
    # 1. 메타데이터 로드
    metadata_path = os.path.join("daily_playlists", "daily_playlists_metadata.json")
    if not os.path.exists(metadata_path):
        print("❌ 메타데이터 파일이 존재하지 않습니다.")
        return
        
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)
        
    day1_meta = next((item for item in metadata_list if item["day"] == 1), None)
    if not day1_meta:
        print("❌ Day 1 메타데이터를 찾을 수 없습니다.")
        return
        
    title = day1_meta["youtube_title"]
    description = day1_meta["youtube_description"]
    tags = day1_meta["youtube_tags"]
    
    # YouTube API limits description to 5000 bytes
    desc_bytes = description.encode('utf-8')
    if len(desc_bytes) > 4800:
        description = desc_bytes[:4800].decode('utf-8', 'ignore') + "\n... (Timestamps truncated due to YouTube limits)"
    
    
    video_path = os.path.join("daily_playlists", "Day1_cozy_rain_cafe", "daily_playlist_day1.mp4")
    if not os.path.exists(video_path):
        print(f"❌ 롱폼 영상 파일이 존재하지 않습니다: {video_path}")
        return
        
    youtube = get_authenticated_service()
    if not youtube:
        print("❌ 유튜브 API 인증에 실패했습니다.")
        return
        
    # 유튜브에 업로드 실행
    # 롱폼이므로 Shorts 해시태그 등은 추가하지 않고 원본 메타데이터를 사용
    # 단, 제목 길이가 100자를 넘는지 확인
    if len(title) > 100:
        title = title[:95] + "..."
        
    # 공개 상태로 바로 업로드 (publish_time=None 이면 비공개로 올라감)
    # 현재 코드는 publish_time이 없으면 비공개로 올리는 로직이므로, 
    # 나중에 수동으로 공개하거나 여기서 코드 수정이 필요할 수 있으나, 일단 안전하게 비공개(private)로 올림.
    upload_video(youtube, title, description, tags, video_path)
    
    print("\n🎉 Day 1 롱폼 영상 업로드가 완료되었습니다! 유튜브 스튜디오에서 확인해주세요.")

if __name__ == "__main__":
    upload_longform()
