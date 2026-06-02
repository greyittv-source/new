import os
import sys
import re
import time
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google import genai
from google.genai import types

sys.stdout.reconfigure(encoding='utf-8')

# OAuth 범위 설정
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube'
]

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1]

def get_authenticated_service():
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        return build('youtube', 'v3', credentials=creds)
    return None

def clean_duplicates_and_optimize():
    print("\n🔍 [메타데이터 최적화] 유튜브 채널 클리닝 및 SEO 최적화 작업을 개시합니다...")
    youtube = get_authenticated_service()
    if not youtube:
        print("❌ 유튜브 API 인증 실패 (token.json 누락)")
        return
        
    client = genai.Client()
    
    try:
        # 1. 채널 업로드 목록 조회
        channels_response = youtube.channels().list(
            mine=True,
            part='contentDetails'
        ).execute()
        
        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        print("🎬 업로드 비디오 목록 로딩 중...")
        playlist_response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet',
            maxResults=30
        ).execute()
        
        items = playlist_response.get('items', [])
        if not items:
            print("ℹ️ 최적화할 비디오가 업로드 목록에 존재하지 않습니다.")
            return
            
        print(f"✅ 총 {len(items)}개의 업로드 항목 발견.")
        
        # 2. 중복 업로드 영상 탐색 및 제거
        print("\n🗑️ 중복 업로드 영상(스팸 필터링 방지) 검사 중...")
        seen_titles = set()
        to_delete = []
        unique_items = []
        
        for item in items:
            title = item['snippet']['title'].strip()
            video_id = item['snippet']['resourceId']['videoId']
            
            # 제목이 동일하거나, 날짜 정보가 포함된 제목이 중복인 경우 제거 대상으로 선정
            if title in seen_titles:
                to_delete.append((video_id, title))
            else:
                seen_titles.add(title)
                unique_items.append(item)
                
        if to_delete:
            print(f"⚠️ 총 {len(to_delete)}개의 중복 또는 중첩 업로드가 감지되었습니다. 일괄 삭제합니다...")
            for vid_id, vid_title in to_delete:
                try:
                    print(f"   [-] 삭제 중: '{vid_title}' (ID: {vid_id})")
                    youtube.videos().delete(id=vid_id).execute()
                    time.sleep(1) # API 레이트 리밋 방지
                except Exception as e:
                    print(f"   ⚠️ 삭제 실패 ({vid_title}): {e}")
            print("✅ 중복 비디오 정리 완료.")
        else:
            print("✅ 중복 비디오 없음. 깨끗한 채널 상태가 확인되었습니다.")

        # 3. 비디오 제목 및 설명 일괄 최적화 (Rename)
        print("\n✨ 기존 동영상 메타데이터 일괄 최적화(Gemini 트렌드 반영) 시작...")
        
        # 5가지 고성능 Lofi 테마 키워드 무작위 배정용 리스트
        lofi_seo_themes = [
            "Cozy Lofi Beats 🌙 | Chill Study & Focus Lofi Mix",
            "Rainy Day Lofi 🌧️ | Relaxing Rain Beats & Study Music",
            "Warm Coffee & Lofi ☕ | Cozy Cafe Lofi Beats to Study/Relax",
            "Midnight Chill Lofi 🌌 | Sleep, Relax & Study Lofi Music",
            "Aesthetic Night Drive 🚗 | Synthwave & Chillwave Road Mix"
        ]
        
        for index, item in enumerate(unique_items):
            title = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']
            
            # 이미 최적화된 키워드 구조를 가졌거나 수동 재업로드 영상은 변경 보류 (단, Vibes Mix는 무조건 교체)
            if "Vibes Mix" not in title and ("Lofi" in title or "Beats" in title) and "Luna's Original" not in title:
                print(f"ℹ️ 건너뛰기 (이미 최적화됨): '{title}' (ID: {video_id})")
                continue
                
            # 날짜 추출 (기존 제목에 있을 경우)
            date_match = re.search(r'\((\d{4}-\d{2}-\d{2})\)', title)
            date_suffix = f" ({date_match.group(1)})" if date_match else f" (Vol. {index + 1})"
            
            # Gemini를 통한 시네마틱 SEO 제목 및 감성 설명란 생성
            try:
                base_theme = lofi_seo_themes[index % len(lofi_seo_themes)]
                
                gemini_prompt = f"""
                당신은 유튜브 최적화 에이전트 루나입니다.
                다음 기본 Lofi 테마 키워드를 바탕으로, 유튜브 알고리즘 노출을 극대화할 수 있는 영문 영상 제목 1개와 한국어 감성 설명글을 작성하세요.
                
                [테마 키워드]: {base_theme}
                
                [제약 조건]:
                1. 결과물 제목은 Lofi, Chill, Study, Sleep, Cozy 등의 핵심 키워드와 이모지(🌙, 🌧️, ☕ 등)를 반드시 포함하여 작성하세요.
                2. 결과물 제목 끝에 날짜 접미사 '{date_suffix}'를 붙이세요. (예: Cozy Lofi Beats 🌙 | Chill Study Mix{date_suffix})
                3. 설명란은 시청자의 감성을 자극하고 소통을 유도하는 문장으로 작성하고, 하단에 #lofi #chill #study #music 해시태그를 포함하세요.
                
                다음 형식으로만 답변을 출력하세요:
                Title: [수정될 비디오 제목]
                Description: [수정될 비디오 설명란]
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=gemini_prompt
                )
                
                res_text = response.text
                new_title = ""
                new_desc = ""
                
                title_match = re.search(r'Title:\s*(.*)', res_text)
                desc_match = re.search(r'Description:\s*(.*)', res_text, re.DOTALL)
                
                if title_match:
                    new_title = title_match.group(1).replace('`', '').strip()
                if desc_match:
                    new_desc = desc_match.group(1).strip()
                    
                if not new_title:
                    new_title = f"{base_theme}{date_suffix}"
                if not new_desc:
                    new_desc = f"오늘 하루도 수고 많으셨습니다. 편안한 Lofi 음악과 함께 힐링 시간을 가져보세요.\n\n#lofi #study #music"
                    
                print(f"📝 업데이트 대기 중:")
                print(f"   - 기존: '{title}'")
                print(f"   - 변경: '{new_title}'")
                
                # 비디오 정보 업데이트 호출
                # status와 snippet을 변경하려면 videos().update를 사용합니다.
                video_details = youtube.videos().list(
                    id=video_id,
                    part='snippet'
                ).execute()
                
                if video_details.get('items'):
                    snippet = video_details['items'][0]['snippet']
                    snippet['title'] = new_title[:100] # 유튜브 제한 100글자
                    snippet['description'] = new_desc
                    # 음악 카테고리 10 설정
                    snippet['categoryId'] = '10'
                    snippet['tags'] = ["lofi", "music", "chill", "study", "playlist", "daily"]
                    
                    youtube.videos().update(
                        part='snippet',
                        body={
                            'id': video_id,
                            'snippet': snippet
                        }
                    ).execute()
                    
                    print(f"✅ 수정 완료 (ID: {video_id})")
                    time.sleep(1.5)
                    
            except Exception as e:
                print(f"❌ '{title}' 업데이트 중 오류 발생: {e}")
                
        print("\n🎉 모든 비디오의 메타데이터 최적화 및 중복 정리 작업이 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 최적화 엔진 동작 실패: {e}")

if __name__ == "__main__":
    clean_duplicates_and_optimize()
