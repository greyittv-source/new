import os
import sys
from tiktok_uploader.upload import upload_video
from upload_tracker import log_upload

sys.stdout.reconfigure(encoding='utf-8')

# .env 환경변수 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

def post_video_to_tiktok(video_path, description):
    session_id = os.getenv("TIKTOK_SESSION_ID")
    
    if not session_id or len(session_id) < 10:
        print("⚠️ [틱톡 봇] .env 파일에 유효한 TIKTOK_SESSION_ID가 없습니다.")
        return False
        
    print(f"\n🚀 [틱톡 봇] 브라우저 세션을 통한 틱톡 비디오 자동 업로드 시도 중...")
    
    try:
        print(f" ⏳ 비디오 업로드 중 (백그라운드 크롬 브라우저 가동)...: {video_path}")
        
        # tiktok-uploader는 세션 ID(브라우저 쿠키 중 'sessionid' 값)를 사용하여 웹에서 올립니다.
        upload_video(video_path,
                     description=description,
                     cookies_list=[{'name': 'sessionid', 'value': session_id, 'domain': '.tiktok.com', 'path': '/'}],
                     headless=True) # 브라우저 창 숨김
                     
        print(f" ✅ 틱톡 게시 완료!")
        log_upload(
            platform="tiktok", content_type="shorts", title=description[:60],
            file_path=video_path, status="success"
        )
        return True
        
    except Exception as e:
        print(f"❌ [틱톡 봇 오류] 업로드 실패: {e}")
        log_upload(
            platform="tiktok", content_type="shorts", title=description[:60],
            file_path=video_path, status="failed", error_message=str(e)
        )
        return False

if __name__ == "__main__":
    print("🤖 루나 틱톡 봇 테스트를 시작합니다.")
