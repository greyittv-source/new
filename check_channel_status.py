import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

sys.stdout.reconfigure(encoding='utf-8')
# 기존 upload 스코프 및 추가 스코프 시도
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube'
]

def get_authenticated_service():
    creds = None
    # 기존 token.json 읽기
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('client_secret.json'):
                print("❌ [오류] client_secret.json 파일이 없습니다.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build('youtube', 'v3', credentials=creds)

def check_channel_videos():
    youtube = get_authenticated_service()
    if not youtube:
        return
        
    print("🔍 유튜브 채널의 최근 업로드 비디오를 검색 중입니다...")
    try:
        # 1. 내 채널의 업로드 플레이리스트 ID 조회
        channels_response = youtube.channels().list(
            mine=True,
            part='contentDetails'
        ).execute()
        
        if not channels_response.get('items'):
            print("❌ 채널 정보를 조회할 수 없습니다.")
            return
            
        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # 2. 최근 업로드된 비디오 리스트 조회 (최대 10개)
        playlist_response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet,status',
            maxResults=10
        ).execute()
        
        items = playlist_response.get('items', [])
        if not items:
            print("ℹ️ 최근 업로드된 동영상이 없습니다.")
            return
            
        video_ids = [item['snippet']['resourceId']['videoId'] for item in items]
        
        # 3. 비디오 상세 정보 조회 (상태, 인코딩 결과 등)
        videos_response = youtube.videos().list(
            id=','.join(video_ids),
            part='snippet,status,processingDetails'
        ).execute()
        
        print("\n=== 최근 업로드 비디오 상태 목록 ===")
        found_error = False
        for video in videos_response.get('items', []):
            title = video['snippet']['title']
            video_id = video['id']
            status = video['status']
            privacy = status.get('privacyStatus')
            upload_status = status.get('uploadStatus')
            rejection_reason = status.get('rejectionReason')
            
            proc_details = video.get('processingDetails', {})
            proc_status = proc_details.get('processingStatus')
            proc_failure = proc_details.get('processingFailureReason')
            
            print(f"\n🎥 제목: {title} (ID: {video_id})")
            print(f"   - 업로드 상태: {upload_status}")
            print(f"   - 공개 상태: {privacy}")
            
            if rejection_reason:
                print(f"   - ❌ 거부 사유: {rejection_reason}")
                found_error = True
            
            if proc_status:
                print(f"   - 처리 상태: {proc_status}")
                if proc_status == 'failed':
                    print(f"   - ❌ 처리 실패 사유: {proc_failure}")
                    found_error = True
            
            # 처리 중단(failed) 상태인 경우 출력강조
            if upload_status == 'failed' or proc_status == 'failed':
                print("   ⚠️ [오류 감지] 해당 영상은 처리 도중 문제가 발생했습니다.")
                found_error = True
                
        if not found_error:
            print("\n✅ 최근 10개 영상 중 처리가 중단되거나 거부된 영상이 발견되지 않았습니다.")
            
    except Exception as e:
        print(f"❌ API 조회 중 오류 발생: {e}")

if __name__ == "__main__":
    check_channel_videos()
