import os
import sys

# Windows에서 cp949 인코딩 충돌 방지를 위해 stdout을 utf-8로 강제 설정
sys.stdout.reconfigure(encoding='utf-8')

try:
    from moviepy.editor import ImageClip, AudioFileClip
except ImportError:
    print("❌ [오류] moviepy 패키지가 설치되지 않았습니다. 'pip install moviepy pillow'를 실행해주세요.")
    sys.exit(1)

def get_ffmpeg_encoder(ffmpeg_bin):
    """NVIDIA GPU 가속(h264_nvenc)이 실제 작동 가능한지 0.1초 프로브 테스트로 자동 감지합니다."""
    import os
    try:
        import subprocess
        probe_file = "test_gpu_probe.mp4"
        test_cmd = [
            ffmpeg_bin, "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64",
            "-t", "0.1", "-c:v", "h264_nvenc", probe_file
        ]
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("🚀 [GPU 감지 성공] NVIDIA GPU 가속 (h264_nvenc) 활성화 완료.")
            if os.path.exists(probe_file):
                try:
                    os.remove(probe_file)
                except Exception:
                    pass
            return "h264_nvenc"
    except Exception:
        pass
    print("ℹ️ GPU 가속(h264_nvenc) 사용 불가. CPU 기반 인코더(libx264)를 사용합니다.")
    return "libx264"

def generate_video(image_path, audio_path, output_path):
    import subprocess
    import moviepy.config as cfg

    print("\n🎬 [비디오 생성기] 최고급 시네마틱 구도(Premium Composition) 렌더링을 시작합니다.")
    print(f" - 🏞️ 배경 이미지: {image_path}")
    print(f" - 🎵 오디오 트랙: {audio_path}")
    print(" ⚠️ 줌인(Ken Burns) 효과 및 프레임 보간으로 인해 렌더링에 1~2분 소요될 수 있습니다...\n")
    
    try:
        # 오디오 트랙 길이 측정
        try:
            with AudioFileClip(audio_path) as clip:
                duration = clip.duration
            print(f"🎵 오디오 총 길이 감지: {duration:.2f}초")
        except Exception as e:
            print(f"⚠️ 오디오 길이를 측정할 수 없어 기본값 50초를 설정합니다: {e}")
            duration = 50.0

        ffmpeg_bin = cfg.get_setting("FFMPEG_BINARY")
        
        # [루나의 집중 모드 - 전체 구도 및 퀄리티 업그레이드]
        # 1. scale & crop: 어떠한 이미지가 들어와도 완벽한 1080x1920(9:16) 비율로 꽉 채움
        # 2. zoompan: 정지 이미지에 생명력을 불어넣는 아주 미세한 줌인(Ken Burns) 효과 (30fps로 부드럽게)
        # 3. vignette: 모서리를 어둡게 눌러주어 중앙 집중도와 영화 같은 무드(Lo-fi) 연출
        # 4. showwaves: 두꺼운 막대그래프 대신, Lo-fi 감성에 가장 잘 어울리는 '세련되고 부드러운 단일 선형(cline)' 파형 적용
        #    화면 가로 전체(1080)를 채우며, 투명도를 주어 배경과 은은하게 섞이도록 디자인
        # 5. overlay: 하단에서 약간 위쪽(H-h-400) 황금 비율 위치에 배치하여 텍스트나 쇼츠 UI에 가리지 않게 함
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p,"
            f"zoompan=z='1.0+it/500':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration * 30) + 100}:s=1080x1920:fps=30,"
            "vignette=angle=PI/4[bg]; "
            "[1:a]showfreqs=s=200x80:mode=bar:ascale=log:fscale=log:colors=white@0.8[raw_freqs]; "
            "[raw_freqs]drawgrid=w=12:h=80:t=4:c=black,colorkey=black:0.1:0.0[wave]; "
            "[bg][wave]overlay=(W-w)/2:H-h-300:shortest=1,"
            "noise=alls=8:allf=t+u,eq=saturation=0.8:contrast=1.1[outv]"
        )
        
        # GPU 가속 코덱 설정 감지
        encoder = get_ffmpeg_encoder(ffmpeg_bin)
        if encoder == "h264_nvenc":
            video_opts = ["-c:v", "h264_nvenc", "-preset", "fast", "-cq", "23"]
        else:
            video_opts = ["-c:v", "libx264", "-preset", "fast", "-crf", "23"]
            
        # -loop 1을 제거하고 zoompan의 d=영상길이 프레임으로 커버함
        # 유튜브 스트리밍/모바일 재생 및 인덱스 복구 오류를 완벽히 막기 위해 -t를 명시하고 -movflags +faststart 옵션을 적용합니다.
        command = [
            ffmpeg_bin,
            "-i", image_path,
            "-i", audio_path,
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "1:a",
        ] + video_opts + [
            "-c:a", "aac",
            "-t", f"{duration:.2f}",
            "-movflags", "+faststart",
            "-y",
            output_path
        ]
        
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        print(f"\n✅ [성공] 최고급 시네마틱 비디오 인코딩이 완료되었습니다! 파일명: {output_path}")
        
    except Exception as e:
        print(f"\n❌ [렌더링 오류] 비디오 합성 중 문제가 발생했습니다:\n{e}")

if __name__ == "__main__":
    IMAGE_FILE = "bg_image.png"
    AUDIO_FILE = "clip.mp3"
    OUTPUT_FILE = "video.mp4"
    
    if not os.path.exists(IMAGE_FILE):
        print(f"❌ [에셋 누락] {IMAGE_FILE} 파일이 없습니다. 아무 이미지나 준비해주세요.")
    elif not os.path.exists(AUDIO_FILE):
        print(f"❌ [에셋 누락] {AUDIO_FILE} 파일이 없습니다. 아무 MP3 음악이나 준비해주세요.")
    else:
        generate_video(IMAGE_FILE, AUDIO_FILE, OUTPUT_FILE)
