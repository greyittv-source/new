import os
import sys
import random
import subprocess
import moviepy.config as cfg
from moviepy.editor import AudioFileClip
import imageio.v3 as iio
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1]

from upload_youtube import get_authenticated_service, upload_video
from insta_bot import post_reels_to_instagram
from tiktok_bot import post_video_to_tiktok
from naver_bot import post_clip_to_naver

def get_ffmpeg_encoder(ffmpeg_bin):
    """NVIDIA GPU 가속(h264_nvenc) 감지"""
    try:
        probe_file = "test_gpu_probe_shorts.mp4"
        test_cmd = [
            ffmpeg_bin, "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64",
            "-t", "0.1", "-c:v", "h264_nvenc", probe_file
        ]
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            if os.path.exists(probe_file):
                try: os.remove(probe_file)
                except: pass
            return "h264_nvenc"
    except Exception:
        pass
    return "libx264"

def get_complementary_color(image_path):
    try:
        img = iio.imread(image_path)
        avg_color = img.mean(axis=0).mean(axis=0)
        if len(avg_color) == 4:
            avg_color = avg_color[:3]
        comp_color = 255 - avg_color
        return "0x{:02x}{:02x}{:02x}".format(int(comp_color[0]), int(comp_color[1]), int(comp_color[2]))
    except Exception as e:
        print(f"색상 추출 실패: {e}")
        return "0x00FFFF"  # fallback cyan

def make_shorts(image_path, audio_path, output_path, title, description, tags, is_debug=False):
    print("\n🎬 [쇼츠 비디오 생성기] 9:16 세로형 쇼츠 렌더링을 시작합니다.")
    print(f" - 배경 이미지: {image_path}")
    print(f" - 오디오: {audio_path}")
    
    ffmpeg_bin = cfg.get_setting("FFMPEG_BINARY")
    encoder = get_ffmpeg_encoder(ffmpeg_bin)
    
    # 원본 배경(background_raw.png)이 존재하면 우선 사용
    dir_name = os.path.dirname(image_path)
    raw_bg = os.path.join(dir_name, "background_raw.png")
    if os.path.exists(raw_bg):
        print("ℹ️ 쇼츠 렌더링에 텍스트가 없는 원본 배경(background_raw.png)을 사용합니다.")
        image_path = raw_bg
        
    try:
        with AudioFileClip(audio_path) as clip:
            total_duration = clip.duration
            
        # 쇼츠 길이 설정 (최대 59초, 최소 15초)
        shorts_duration = min(total_duration, 59.0)
        start_time = 0.0
        
        # 오디오가 충분히 길다면 랜덤한 하이라이트 구간(중반부) 추출 (15초 여유 남기기)
        if total_duration > 60:
            start_time = random.uniform(0, total_duration - shorts_duration)
            
        print(f"🎵 쇼츠 오디오 추출 구간: {start_time:.1f}초 ~ {start_time + shorts_duration:.1f}초 (총 {shorts_duration:.1f}초)")
        
        comp_color = get_complementary_color(image_path)
        print(f"🎨 배경 보색 추출 완료: {comp_color}")
        
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p,"
            f"zoompan=z='1.0+it/500':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(shorts_duration * 30) + 100}:s=1080x1920:fps=30,"
            "vignette=angle=PI/4,"
            "noise=alls=8:allf=t+u,eq=saturation=0.8:contrast=1.1,"
            "drawtext=text='L O F I':fontcolor=white:borderw=4:bordercolor=black@0.9:alpha='0.6+0.4*abs(sin(t*3))':fontsize=120:x=(w-text_w)/2:y=(h-text_h)/2-250:shadowcolor=black@0.8:shadowx=6:shadowy=6,"
            f"drawtext=text='S H O R T S':fontcolor={comp_color}:borderw=3:bordercolor=black@0.9:alpha='0.5+0.5*abs(sin(t*3))':fontsize=70:x=(w-text_w)/2:y=(h-text_h)/2-100:shadowcolor=black@0.8:shadowx=4:shadowy=4,"
            "drawgrid=w=iw:h=4:t=1:c=black@0.1,"
            "chromashift=cbh=-3:crh=3[bg_vid]; "
            
            # 오디오 분배 (파형용, 출력용)
            "[1:a]asplit=2[a_wave][a_out]; "
            
            # 파형 시각화 (두꺼운 레트로 막대그래프 + 막대 사이 간격 넓히기)
            "[a_wave]showfreqs=s=25x100:mode=bar:colors=white:ascale=log,scale=450x100:flags=neighbor,"
            "drawgrid=w=18:h=100:t=6:c=black,colorkey=black:0.1:0.0,"
            "format=yuva420p,colorchannelmixer=aa=0.8,"
            "fade=t=in:st=0:d=2.0:alpha=1,fade=t=out:st=13.0:d=2.0:alpha=1[wave]; "
            
            # 파형 오버레이 (화면 하단)
            "[bg_vid][wave]overlay=(W-w)/2:H-h-200[outv]; "
            
            # 오디오 페이드 인/아웃
            f"[a_out]afade=t=in:st=0:d=1.5,afade=t=out:st={shorts_duration-1.5:.2f}:d=1.5[outa]"
        )
        
        if encoder == "h264_nvenc":
            video_opts = ["-c:v", "h264_nvenc", "-preset", "fast", "-cq", "23"]
        else:
            video_opts = ["-c:v", "libx264", "-preset", "fast", "-crf", "23"]
            
        command = [
            ffmpeg_bin,
            "-i", image_path,
            "-ss", str(start_time),
            "-i", audio_path,
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "[outa]",
        ] + video_opts + [
            "-c:a", "aac",
            "-t", f"{shorts_duration:.2f}",
            "-movflags", "+faststart",
            "-y",
            output_path
        ]
        
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(f"✅ 쇼츠 렌더링 완료: {output_path}")
        
        try:
            if os.name == 'nt':
                os.startfile(output_path)
        except Exception:
            pass
        
        if not is_debug:
            youtube = get_authenticated_service()
            if youtube:
                print("⏳ 쇼츠 유튜브 업로드 진행 중...")
                
                # 쇼츠를 위한 태그 및 설명 강화
                shorts_title = f"{title} #Shorts"
                shorts_description = f"{description}\n\n⚠️ 본 영상의 음악과 이미지는 모두 AI 기술을 활용하여 자동 생성(창작)되었습니다.\n(This video's music and images were created using AI technology.)\n\n#Shorts #Lofi #GreyitTV #StudyMusic"
                shorts_tags = tags + ["Shorts", "Lofi", "study", "relax"]
                
                upload_video(youtube, shorts_title, shorts_description, shorts_tags, output_path)
                print(f"✅ 유튜브 쇼츠 업로드 완료!")
                
            print("⏳ 인스타그램 릴스 업로드 진행 중...")
            post_reels_to_instagram(output_path, shorts_description)
            
            print("⏳ 틱톡 쇼츠 업로드 진행 중...")
            post_video_to_tiktok(output_path, shorts_description)

            # 네이버 클립 자동 업로드
            print(f"\n네이버 클립 업로드 중...")
            try:
                post_clip_to_naver(output_path, title, shorts_description, shorts_tags)
                print(f"\n[네이버 클립 업로드 성공!]")
            except Exception as e:
                print(f"\n[네이버 클립 업로드 실패]: {e}")

            print(f"✅ 모든 SNS 플랫폼(유튜브, 인스타, 틱톡, 네이버클립) 자동 업로드 파이프라인 완료!")
        else:
            print("ℹ️ [디버그 모드] 쇼츠 유튜브 업로드를 건너뜁니다.")
            
    except Exception as e:
        print(f"❌ 쇼츠 생성 중 오류 발생: {e}")

if __name__ == "__main__":
    # 테스트용 단독 실행
    is_debug = "debug" in sys.argv
    if os.path.exists("bg_image.png") and os.path.exists("clip.mp3"):
        make_shorts("bg_image.png", "clip.mp3", "test_shorts.mp4", "Test Lofi Vibes", "A test shorts video.", ["lofi"], is_debug=is_debug)
    else:
        print("테스트용 bg_image.png 또는 clip.mp3가 없습니다.")
