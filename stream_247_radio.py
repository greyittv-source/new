import os
import sys
import glob
import subprocess
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

def start_247_radio():
    print("📻 [Greyit TV] 24/7 Lofi Radio 스트리밍 시작 준비 중...")
    
    # 1. 환경변수 및 스트림 키 확인
    load_dotenv()
    stream_key = os.getenv("YOUTUBE_STREAM_KEY")
    if not stream_key:
        print("❌ 오류: .env 파일에 YOUTUBE_STREAM_KEY 가 없습니다.")
        print("   유튜브 라이브 관제실(YouTube Live Control Room)에서 스트림 키를 복사하여 .env에 추가해주세요.")
        print("   예: YOUTUBE_STREAM_KEY=abcd-efgh-1234-5678-ijkl")
        return
        
    # 2. 재생할 비디오 목록 탐색
    video_files = glob.glob("daily_playlists/*/daily_playlist_day*.mp4")
    if not video_files:
        print("❌ 오류: 스트리밍할 재생목록 비디오(daily_playlist_day*.mp4)를 찾을 수 없습니다.")
        return
        
    print(f"🎵 총 {len(video_files)}개의 플레이리스트 비디오를 찾았습니다.")
    
    # 3. concat 파일(stream_list.txt) 생성
    concat_file = "stream_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for vf in video_files:
            # 절대 경로나 이스케이프 처리된 상대 경로 권장
            safe_path = vf.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")
            
    print(f"📝 {concat_file} 파일 생성 완료.")
    
    # 4. FFmpeg 송출 커맨드 구성
    # -re : 실시간(Real-time) 속도로 읽기
    # -stream_loop -1 : 무한 반복
    # -f concat : 여러 파일을 하나로 묶음
    # -c copy : 영상/오디오 재인코딩 없이 원본 그대로 복사 전송 (CPU 점유율 거의 0%)
    # -f flv : 유튜브 RTMP 포맷
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    ffmpeg_cmd = [
        "ffmpeg",
        "-re",
        "-stream_loop", "-1",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        "-f", "flv",
        rtmp_url
    ]
    
    print("🚀 스트리밍을 시작합니다! (종료하려면 Ctrl+C를 누르세요)")
    print("-" * 50)
    
    try:
        # Popen으로 실행하여 실시간 로그를 볼 수 있게 함
        subprocess.run(ffmpeg_cmd)
    except KeyboardInterrupt:
        print("\n🛑 스트리밍이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ FFmpeg 실행 오류: {e}")

if __name__ == "__main__":
    start_247_radio()
