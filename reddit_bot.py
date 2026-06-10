import os
import sys
import praw
from praw.exceptions import RedditAPIException

sys.stdout.reconfigure(encoding='utf-8')

# .env 환경변수 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

def get_reddit_instance():
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent="GreyitTV:LunaBot:1.0"
        )
        # 인증 확인
        reddit.user.me()
        return reddit
    except Exception as e:
        print(f"⚠️ [레딧 봇] 인증 실패. .env 파일의 REDDIT API 키를 확인해주세요: {e}")
        return None

def post_video_to_reddit(title, video_path, thumbnail_path, comment_text, subreddit_name="LofiHipHop"):
    print(f"\n🚀 [레딧 봇] '{subreddit_name}' 커뮤니티에 소프트 프로모션 시작...")
    
    reddit = get_reddit_instance()
    if not reddit:
        return False
        
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        print(f" ⏳ 비디오 업로드 중 (Native Video): {video_path}")
        # PRAW의 submit_video 사용 (레딧 자체 비디오 호스팅)
        submission = subreddit.submit_video(
            title=title, 
            video_path=video_path,
            thumbnail_path=thumbnail_path
        )
        print(f" ✅ 게시 완료! (URL: https://reddit.com{submission.permalink})")
        
        # 첫 번째 낚시줄(댓글) 달기
        if comment_text:
            print(f" ⏳ 첫 번째 유도 댓글(Youtube Link) 작성 중...")
            comment = submission.reply(comment_text)
            print(f" ✅ 댓글 작성 완료!")
            
        return True
        
    except RedditAPIException as e:
        print(f"❌ [레딧 API 에러] {e}")
        return False
    except Exception as e:
        print(f"❌ [에러] 레딧 업로드 중 알 수 없는 오류: {e}")
        return False

if __name__ == "__main__":
    print("🤖 루나 레딧 봇 테스트를 시작합니다.")
    print("사용하시려면 .env 파일에 다음 정보를 기입해야 합니다:")
    print("REDDIT_CLIENT_ID=...")
    print("REDDIT_CLIENT_SECRET=...")
    print("REDDIT_USERNAME=...")
    print("REDDIT_PASSWORD=...")
