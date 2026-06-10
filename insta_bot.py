import os
import sys
from instagrapi import Client
import moviepy.editor as mp
import moviepy
moviepy.VideoFileClip = mp.VideoFileClip

sys.stdout.reconfigure(encoding='utf-8')

# .env 환경변수 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

def post_reels_to_instagram(video_path, caption):
    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")
    session_id = os.getenv("IG_SESSIONID")
    
    if not username:
        print("⚠️ [인스타 봇] .env 파일에 IG_USERNAME이 없습니다.")
        return False
        
    print(f"\n🚀 [인스타 봇] '{username}' 계정으로 인스타그램 릴스 업로드 시도 중...")
    
    try:
        cl = Client()
        session_file = f"insta_session_{username}.json"
        
        if session_id:
            print("🔑 IG_SESSIONID 쿠키로 다이렉트 로그인 시도 중...")
            cl.login_by_sessionid(session_id)
            cl.dump_settings(session_file)
        elif os.path.exists(session_file):
            print("🔑 기존 저장된 세션 파일로 로그인 중...")
            cl.load_settings(session_file)
            cl.login(username, password)
        else:
            print("🔑 아이디/비밀번호로 로그인 중...")
            cl.login(username, password)
            cl.dump_settings(session_file)
            
        print(f" ⏳ 비디오 업로드 중...: {video_path}")
        # clip_upload가 릴스(Reels) 업로드 함수입니다.
        media = cl.clip_upload(video_path, caption)
        
        print(f" ✅ 인스타 릴스 게시 완료! (URL: https://www.instagram.com/reel/{media.code})")
        return True
        
    except Exception as e:
        print(f"❌ [인스타 봇 오류] 업로드 실패: {e}")
        print("💡 (팁) 스마트폰 인스타그램 앱에 들어가 '본인 맞음' 버튼을 누르거나, 비밀번호를 변경해야 할 수 있습니다.")
        if os.path.exists(session_file):
            os.remove(session_file)
        return False

if __name__ == "__main__":
    print("🤖 루나 인스타 봇 테스트를 시작합니다.")
