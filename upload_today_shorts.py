import os
import sys
import json
from datetime import datetime
from upload_youtube import get_authenticated_service, upload_video

sys.stdout.reconfigure(encoding='utf-8')

def upload_today_shorts():
    print("==================================================")
    print("🚀 [수동 런칭] 오늘(Day 1) 쇼츠 전체 플랫폼 업로드 시작")
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
    
    video_path = os.path.join("daily_playlists", "Day1_cozy_rain_cafe", "shorts_day1.mp4")
    if not os.path.exists(video_path):
        print(f"❌ 쇼츠 파일이 존재하지 않습니다: {video_path}")
        return
        
    import re
    base_desc_no_ts = re.sub(r"\[Timestamps\].*", "", description, flags=re.DOTALL).strip()
    
    shorts_title = f"{title} #Shorts"
    if len(shorts_title) > 100:
        shorts_title = shorts_title[:95] + "..."
        
    shorts_description = f"{base_desc_no_ts}\n\n#Shorts #Lofi #GreyitTV"
    shorts_tags = tags + ["Shorts", "Lofi"]
    
    # YouTube Upload
    print("\n[1/4] 유튜브 쇼츠 업로드 가동 중... (이미 성공하여 패스합니다)")

    # Instagram Upload
    print("\n[2/4] 인스타그램 릴스 가동 중... (불안정하여 임시 패스합니다)")

    # TikTok Upload
    print("\n[3/4] 틱톡 숏폼 가동 중...")
    try:
        from tiktok_bot import post_video_to_tiktok
        tiktok_desc = f"Enjoy this aesthetic lofi vibe 🎧✨ {shorts_description[:100]}... #lofi #aesthetic #GreyitTV"
        result_tt = post_video_to_tiktok(video_path, tiktok_desc)
        if result_tt: print("✅ 틱톡 업로드 성공!")
        else: print("❌ 틱톡 업로드 실패.")
    except Exception as e:
        print(f"❌ 틱톡 오류: {e}")

    # Naver Clip Upload
    print("\n[4/4] 네이버 클립 가동 중...")
    try:
        from naver_bot import post_clip_to_naver
        result_nv = post_clip_to_naver(video_path, shorts_title, shorts_description, shorts_tags)
        if result_nv: print("✅ 네이버 클립 업로드 성공!")
        else: print("❌ 네이버 클립 업로드 실패.")
    except Exception as e:
        print(f"❌ 네이버 오류: {e}")

    print("\n🎉 모든 쇼츠 플랫폼 업로드 과정이 완료되었습니다!")

if __name__ == "__main__":
    upload_today_shorts()
