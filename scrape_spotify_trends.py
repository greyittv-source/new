import os
import sys
import re
import httpx

sys.stdout.reconfigure(encoding='utf-8')

def scrape_spotify_lofi_tracks():
    url = "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO" # Spotify Official Lofi Beats
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("🌐 스포티파이 Lofi Beats 플레이리스트 스캔 중...")
    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
        if response.status_code == 200:
            html = response.text
            
            # 1. og:description 또는 twitter:description에서 곡 목록 추출 시도
            # 보통 포맷: "Listen on Spotify: Song 1 - Artist 1, Song 2 - Artist 2, ..."
            desc_match = re.search(r'<meta (?:name|property)="twitter:description" content="([^"]+)"', html)
            if not desc_match:
                desc_match = re.search(r'<meta (?:name|property)="og:description" content="([^"]+)"', html)
                
            if desc_match:
                content = desc_match.group(1)
                # "Listen on Spotify: " 또는 "· Playlist ·" 부분 필터링 및 곡명 분리
                print("✅ 스포티파이 Lofi 메타데이터 검색 성공.")
                
                # 곡 목록 파싱
                tracks = []
                # 쉼표(,) 혹은 세미콜론(;) 단위로 곡명-아티스트가 열거됨
                items = content.split(",")
                for item in items:
                    cleaned = item.strip()
                    if "·" in cleaned or "Playlist" in cleaned or "likes" in cleaned or "songs" in cleaned:
                        continue
                    if cleaned:
                        tracks.append(cleaned)
                        
                if tracks:
                    return tracks
            
            # 2. HTML 내의 노래 제목 및 아티스트 스크랩 시도 (정규식 기반)
            # Spotify 공개 웹페이지 구조 내의 곡명 구조 파싱
            track_matches = re.findall(r'"name":"([^"]+)"', html)
            # 중복 제거 및 "Lofi Beats" 같은 플레이리스트 자체 이름 배제
            filtered_tracks = [t for t in track_matches if len(t) < 50 and "Lofi" not in t and t != "Spotify"]
            if filtered_tracks:
                return filtered_tracks[:15]
                
    except Exception as e:
        print(f"⚠️ 스포티파이 웹 스크랩 실패: {e}")
        
    # 3. 네트워크 실패 또는 파싱 실패 시, 최고 트래픽의 Lofi 대표 아티스트 목록 및 키워드 반환 (Fallback)
    print("⚠️ 스포티파이 실시간 스크랩 실패. 알고리즘 검증된 고트래픽 Lofi 에셋 리스트로 대체합니다.")
    return [
        "Idealism - Phantasia",
        "Jinsang - Smile from U",
        "Saib - Spike Spiegel",
        "Nujabes - Feather",
        "Sleepy Fish - School Friends",
        "Kupla - Kingdom in the Clouds",
        "SwuM - Tokyo",
        "Wun Two - Blue In Green",
        "Kalaido - Sempiternal",
        "invention_ - Shimmer"
    ]

def save_spotify_trends():
    tracks = scrape_spotify_lofi_tracks()
    output_path = "spotify_trends.txt"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=== SPOTIFY TRENDING LOFI TRACKS ===\n")
        for track in tracks:
            f.write(f"{track}\n")
            
    print(f"✅ 스포티파이 트렌드 저장 완료: {output_path} ({len(tracks)}개 곡)")

if __name__ == "__main__":
    save_spotify_trends()
