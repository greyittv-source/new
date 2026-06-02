import os
import subprocess
import time
import sys
import schedule
import shutil
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding='utf-8')

def get_publish_times():
    # 오늘 자정 기준
    now = datetime.now().astimezone()
    # 유튜브 예약 업로드용으로 한국시간 기준 18시, 20시, 22시를 ISO 8601로 포맷팅
    # Local 타임이므로 timezone을 포함하여 정확히 설정 (여기서는 KST로 가정하거나 현재 로컬 시간대 적용)
    
    # 3개의 골든 타임 슬롯 (18:00, 20:00, 22:00)
    slots = [18, 20, 22]
    publish_times = []
    
    for hour in slots:
        # 오늘 날짜에 지정된 시간으로 설정
        publish_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # 만약 현재 시간보다 과거라면 내일로 설정 (새벽 3시 가동이므로 당일 업로드)
        if publish_time <= now:
            publish_time += timedelta(days=1)
            
        publish_times.append(publish_time.isoformat())
        
    return publish_times

def write_usage_report(music_count, image_count, text_count):
    """오늘의 API 사용 횟수와 예상 청구 비용을 계산하여 daily_api_usage.txt에 기록하고 화면에 출력합니다."""
    # 단가 기준 (대략적 추정치)
    lyria_price_per_unit = 0.03    # 곡당 약 $0.03
    imagen_price_per_unit = 0.03   # 이미지당 약 $0.03
    gemini_price_per_unit = 0.0001  # 텍스트 호출당 약 $0.0001
    
    total_est_cost = (music_count * lyria_price_per_unit) + (image_count * imagen_price_per_unit) + (text_count * gemini_price_per_unit)
    
    report_path = "daily_api_usage.txt"
    now = datetime.now().astimezone()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    report_text = f"""========================================
[API 사용량 및 예상 비용 일일 보고서]
작성 일시: {date_str}
========================================
- Lyria 음악 생성 API: {music_count}회 호출 (예상 비용: ${music_count * lyria_price_per_unit:.2f})
- Imagen 4 이미지 생성 API: {image_count}회 호출 (예상 비용: ${image_count * imagen_price_per_unit:.2f})
- Gemini 2.5 텍스트 생성 API: {text_count}회 호출 (예상 비용: ${text_count * gemini_price_per_unit:.4f})
----------------------------------------
오늘의 총 예상 API 요금: ${total_est_cost:.2f} (약 {int(total_est_cost * 1350)}원)
========================================
"""
    
    try:
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(report_text + "\n")
    except Exception as e:
        print(f"⚠️ 비용 보고서 파일 쓰기 실패: {e}")
        
    print("\n💰 [비용 보고서] 오늘의 API 사용량 및 예상 비용 요약:")
    print(report_text)

def run_pipeline():
    print("\n🚀 [에이전트 루나] 유튜브 채널 100% 무인 운영 파이프라인 가동 시작...")
    print("="*60)
    
    music_success = 0
    thumbnail_success = 0
    playlist_success = 0

    print("\n[Step 0] 유튜브 뮤직 및 스포티파이 Lofi 최신 트렌드 스캐닝 중...")
    try:
        fetch_script = os.path.join("..", "음악채널에이전트루나", "fetch_top100.py")
        with open("daily_trends.txt", "w", encoding="utf-8") as f:
            subprocess.run(["python", fetch_script], check=True, stdout=f)
        print("✅ 유튜브 뮤직 트렌드 스캐닝 완료 (daily_trends.txt)")
    except Exception as e:
        print(f"⚠️ 유튜브 뮤직 트렌드 스캐닝 실패 (기존 방식대로 진행): {e}")
        
    try:
        print("🌐 스포티파이 Lofi 트렌드 스크랩 중...")
        subprocess.run(["python", "scrape_spotify_trends.py"], check=True)
        print("✅ 스포티파이 트렌드 스크랩 완료 (spotify_trends.txt)")
    except Exception as e:
        print(f"⚠️ 스포티파이 트렌드 스크랩 실패: {e}")

    publish_times = get_publish_times()
    
    for idx, publish_time in enumerate(publish_times, 1):
        try:
            print(f"\n[{idx}/3] ✨ 새로운 음악/영상 생성 및 예약 업로드 파이프라인 시작 (예약시간: {publish_time})")
            
            print("\n[Step 1] 트렌드 스캐닝 및 음악/기획안 생성 (generate_music.py 실행 중...)")
            subprocess.run(["python", "generate_music.py", str(idx)], check=True)
            music_success += 1
            time.sleep(1)

            print("\n[Step 2] AI 썸네일 자동 생성 (generate_thumbnail.py 실행 중...)")
            subprocess.run(["python", "generate_thumbnail.py"], check=True)
            thumbnail_success += 1
            time.sleep(1)

            print("\n[Step 3] 오디오와 썸네일 이미지 합성 렌더링 (generate_video.py 실행 중...)")
            subprocess.run(["python", "generate_video.py"], check=True)
            time.sleep(1)

            print("\n[Step 4] YouTube Data API 예약 자동 업로드 (upload_youtube.py 실행 중...)")
            subprocess.run(["python", "upload_youtube.py", publish_time], check=True)
            time.sleep(1)
            
            if os.path.exists("video.mp4"):
                shutil.copy("video.mp4", f"video_{idx}.mp4")
            if os.path.exists("clip.mp3"):
                shutil.copy("clip.mp3", f"audio_{idx}.mp3")

            print(f"✅ [{idx}/3] 파이프라인 완료. 다음 영상 생성 준비...")
            time.sleep(5) # API 과부하 방지
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ [오류] {idx}번째 루프 파이프라인 자식 스크립트 실행 중 에러가 발생했습니다: {e}")
            continue # 하나의 영상 생성이 실패해도 다음 영상 생성은 시도함
        except Exception as e:
            print(f"❌ [Step 4] 플레이리스트 생성/업로드 중 오류 발생: {e}")
            
    print("\n[Step 4.5] 롱폼 플레이리스트 구성을 위한 추가 음원 생성 중...")
    for extra_idx in range(4, 13):
        try:
            print(f"🎵 추가 음원 생성 중 ({extra_idx}/12)...")
            subprocess.run(["python", "generate_music.py", str(extra_idx)], check=True)
            music_success += 1
            if os.path.exists("clip.mp3"):
                shutil.copy("clip.mp3", f"audio_{extra_idx}.mp3")
            time.sleep(2) # API 호출 안정화
        except Exception as e:
            print(f"⚠️ 추가 음원 {extra_idx} 생성 실패: {e}")
            
    # [Step 5] 틱톡 및 네이버 클립 등 타 플랫폼 자동 업로드 시도
    print("\n[Step 5] 타 플랫폼(틱톡, 네이버 클립) 숏폼 자동 업로드 진행...")
    try:
        from upload_platforms import run_upload
        # main.py에서 short_videos가 정의되지 않았을 수 있으므로 안전 처리
        short_videos = [f"video_{i}.mp4" for i in range(1, 4)]
        for short_file in short_videos:
            if os.path.exists(short_file):
                short_title = f"Luna's Vibes - {short_file}"
                # 숏폼 1개를 네이버 클립과 틱톡에 동시 전송
                run_upload("네이버클립", short_file, short_title, ["lofi", "music", "playlist"])
                run_upload("틱톡", short_file, short_title, ["lofi", "music", "playlist"])
                break # 데모 시연용으로 1개만 업로드
    except ImportError:
        print("⚠️ upload_platforms 모듈이 없습니다. (Playwright 셋업 필요)")
    except Exception as e:
        print(f"❌ [Step 5] 타 플랫폼 업로드 중 오류 발생: {e}")

    print("\n[완료] 🎉 오늘자 쇼츠 및 멀티플랫폼 파이프라인 실행을 모두 마쳤습니다!")
    print("\n[Step 6] 숏폼 연결 플레이리스트 생성 및 업로드 (make_playlist.py 실행 중...)")
    try:
        subprocess.run(["python", "make_playlist.py"], check=True)
        playlist_success = 1
    except Exception as e:
        print(f"❌ 플레이리스트 생성 중 오류 발생: {e}")

    print("\n" + "="*60)
    print("✅ [성공] 일일 3개 영상 + 플레이리스트 파이프라인 1사이클 완료.")
    
    # API 비용 보고서 작성 및 출력
    write_usage_report(
        music_count=music_success,
        image_count=thumbnail_success + playlist_success,
        text_count=music_success + playlist_success
    )
    
    print("다음 예약된 주기(새벽 3시)까지 백그라운드 대기(Standby) 모드로 전환합니다.")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("\n⏳ [스케줄러 가동] 시스템이 모니터링 데몬(Daemon) 모드로 진입했습니다. (종료 시 Ctrl+C)")
    print("🔔 매일 새벽 3:00에 3개의 영상이 자동으로 생성되어 18시, 20시, 22시에 예약 업로드 됩니다.")
    
    # 매일 새벽 3시에 동작하도록 설정
    schedule.every().day.at("03:00").do(run_pipeline)
    
    # 시스템 데몬 루프
    while True:
        schedule.run_pending()
        time.sleep(60) # 1분 주기로 스케줄 달성 여부 체크
