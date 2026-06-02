import os
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

sys.stdout.reconfigure(encoding='utf-8')
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube'
]

def get_authenticated_service():
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        return build('youtube', 'v3', credentials=creds)
    return None

def analyze_videos():
    youtube = get_authenticated_service()
    if not youtube:
        print("❌ 인증 정보(token.json)를 찾을 수 없습니다.")
        return
        
    try:
        # 1. 내 채널의 업로드 플레이리스트 ID 조회
        channels_response = youtube.channels().list(
            mine=True,
            part='contentDetails,statistics'
        ).execute()
        
        channel_stat = channels_response['items'][0]['statistics']
        print(f"📈 채널 요약 통계:")
        print(f"   - 총 구독자 수: {channel_stat.get('subscriberCount')}")
        print(f"   - 총 조회수: {channel_stat.get('viewCount')}")
        print(f"   - 총 업로드 동영상 수: {channel_stat.get('videoCount')}")
        
        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # 2. 최근 업로드된 비디오 리스트 조회 (최대 10개)
        playlist_response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet',
            maxResults=15
        ).execute()
        
        items = playlist_response.get('items', [])
        if not items:
            print("ℹ️ 최근 업로드된 동영상이 없습니다.")
            return
            
        video_ids = [item['snippet']['resourceId']['videoId'] for item in items]
        
        # 3. 비디오 상세 정보 및 통계 조회
        videos_response = youtube.videos().list(
            id=','.join(video_ids),
            part='snippet,statistics'
        ).execute()
        
        print("\n📊 [영상별 상세 성과 분석 데이터]")
        print(f"{'업로드 날짜':<12} | {'조회수':<6} | {'좋아요':<6} | {'댓글':<4} | {'영상 제목'}")
        print("-" * 80)
        
        for video in videos_response.get('items', []):
            title = video['snippet']['title']
            published_at = video['snippet']['publishedAt'][:10] # YYYY-MM-DD
            stats = video.get('statistics', {})
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            
            print(f"{published_at:<12} | {views:<6} | {likes:<6} | {comments:<4} | {title}")
            
    except Exception as e:
        print(f"❌ 분석 실패: {e}")

if __name__ == "__main__":
    analyze_videos()
