import os
import subprocess
import shutil
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("🎵 1시간 플레이리스트용 추가 음원 생성 중 (audio_4 ~ audio_12)...")
    for extra_idx in range(4, 13):
        if os.path.exists(f"audio_{extra_idx}.mp3"):
            print(f"ℹ️ audio_{extra_idx}.mp3 파일이 이미 존재하여 건너뜁니다.")
            continue
        try:
            print(f"🎵 추가 음원 생성 중 ({extra_idx}/12)...")
            subprocess.run(["python", "generate_music.py", str(extra_idx)], check=True)
            if os.path.exists("clip.mp3"):
                shutil.copy("clip.mp3", f"audio_{extra_idx}.mp3")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ 추가 음원 {extra_idx} 생성 실패: {e}")

    print("\n🎬 1시간 플레이리스트 비디오 렌더링 및 예약 업로드 시작...")
    # make_playlist.py를 아규먼트 없이 구동하여 1시간짜리 비디오를 생성하고 유튜브에 업로드합니다.
    try:
        subprocess.run(["python", "make_playlist.py"], check=True)
        print("✅ 1시간 플레이리스트 제작 및 유튜브 예약 업로드 완료!")
    except Exception as e:
        print(f"❌ 1시간 플레이리스트 생성 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
