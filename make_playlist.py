import os
import subprocess
from datetime import datetime, timedelta
import sys
import io
from PIL import Image
from google import genai
from google.genai import types

sys.stdout.reconfigure(encoding='utf-8')

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1]

import moviepy.config as cfg
try:
    from upload_youtube import get_authenticated_service, upload_video
except ImportError:
    print("❌ upload_youtube.py를 찾을 수 없습니다.")
    sys.exit(1)

def generate_playlist_thumbnail():
    print("\n[플레이리스트] 16:9 전용 배경 이미지 생성 중...")
    client = genai.Client()
    
    import random
    environments = [
        "a cozy rainy day by the window",
        "a beautiful golden hour sunset over the city",
        "a quiet snowy evening in a wooden cabin",
        "a starry night sky with a glowing desk lamp",
        "a warm autumn afternoon in a vintage cafe",
        "a peaceful morning breeze in a greenhouse",
        "a neon-lit cyberpunk city alley at midnight"
    ]
    random_env = random.choice(environments)
    image_prompt = f"A cinematic, relaxing, wide landscape suitable for a lofi music playlist background. Featuring {random_env}, beautiful scenery, soft lighting, highly detailed lofi aesthetic, 16:9 aspect ratio."
    if os.path.exists("lyrics_and_plan.txt"):
        with open("lyrics_and_plan.txt", "r", encoding="utf-8") as f:
            plan_text = f.read()
        extract_prompt = f"다음 기획안에서 썸네일 이미지 생성을 위한 영문 프롬프트(미드저니/DALL-E용 프롬프트)만 추출해서 영문으로 1문장으로만 답해줘. 부가 설명 절대 금지.\n\n{plan_text}"
        try:
            prompt_response = client.models.generate_content(model="gemini-1.5-flash", contents=extract_prompt)
            image_prompt = prompt_response.text.strip()
            print(f"👉 추출된 기본 프롬프트: {image_prompt}")
        except Exception:
            pass

    # Imagen 4로 16:9 생성
    try:
        result = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=image_prompt + " wide landscape, highly detailed, atmospheric",
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="16:9" # 롱폼용 가로 비율
            )
        )
        if result.generated_images:
            image_bytes = result.generated_images[0].image.image_bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype("arialbd.ttf", 150)
            except:
                font = ImageFont.load_default()
                
            text = "P L A Y L I S T"
            
            # 텍스트 크기 측정 (textbbox 사용)
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_w = right - left
            text_h = bottom - top
            
            W, H = image.size
            x = (W - text_w) / 2
            y = (H - text_h) / 2
            
            # 그림자 (Shadow)
            draw.text((x + 5, y + 5), text, font=font, fill=(0, 0, 0, 180))
            # 메인 텍스트
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 230))

            image.save("playlist_bg.png", "PNG")
            print("✅ 16:9 썸네일 생성 및 텍스트 추가 완료 (playlist_bg.png)")
            return "playlist_bg.png"
    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")
    return None

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

def create_and_upload_playlist():
    print("\n🎬 [플레이리스트 제작] 16:9 롱폼 플레이리스트 영상을 생성합니다...")
    
    audios = [f"audio_{i}.mp3" for i in range(1, 16)]
    existing_audios = [a for a in audios if os.path.exists(a)]
    
    if not existing_audios:
        print("❌ 연결할 오디오 파일(audio_*.mp3)이 없습니다.")
        return
        
    ffmpeg_bin = cfg.get_setting("FFMPEG_BINARY")
    
    # 1. 오디오 병합 (목표 시간: 기본 60분/3600초)
    print("\n[플레이리스트] 오디오 길이 계산 및 병합 리스트 생성 중...")
    from moviepy.editor import AudioFileClip
    import math
    
    total_original_duration = 0
    audio_durations = []
    for a in existing_audios:
        try:
            with AudioFileClip(a) as clip:
                audio_durations.append(clip.duration)
                total_original_duration += clip.duration
        except Exception:
            audio_durations.append(30.0)
            total_original_duration += 30.0
            
    is_debug = "debug" in sys.argv or os.environ.get("DEBUG_PLAYLIST") == "True"
    target_duration = 300.0 if is_debug else 3600.0  # 디버그 모드일 때는 5분으로 단축
    
    required_loops = 1
    if total_original_duration > 0 and total_original_duration < target_duration:
        required_loops = math.ceil(target_duration / total_original_duration)
        print(f"👉 원본 오디오 총 길이: {total_original_duration:.1f}초 -> {target_duration/60:.1f}분을 채우기 위해 {required_loops}회 반복(Loop)합니다.")
    else:
        print(f"👉 원본 오디오 총 길이: {total_original_duration:.1f}초 (반복 없이 진행)")
        
    # 실제 플레이리스트 총 시간 계산
    playlist_total_duration = total_original_duration * required_loops

    # 곡 제목 읽기 및 자막(SRT) 생성
    print("\n[플레이리스트] 곡 제목 자막(SRT) 생성 중...")
    def format_srt_time(seconds):
        h, m, s = int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        
    srt_content = ""
    srt_index = 1
    current_time = 0.0
    
    titles = []
    for i in range(1, len(existing_audios) + 1):
        title_file = f"title_{i}.txt"
        t = f"Luna's Original Track {i}"
        if os.path.exists(title_file):
            with open(title_file, "r", encoding="utf-8") as tf:
                t = tf.read().strip()
        titles.append(t)
        
    for loop in range(required_loops):
        for i, duration in enumerate(audio_durations):
            start_sec = current_time
            end_sec = current_time + 8.0 # 8초간 표시
            if end_sec > current_time + duration:
                end_sec = current_time + duration
                
            srt_content += f"{srt_index}\n"
            srt_content += f"{format_srt_time(start_sec)} --> {format_srt_time(end_sec)}\n"
            srt_content += f"🎵 Now Playing: {titles[i]}\n\n"
            
            srt_index += 1
            current_time += duration

    with open("playlist.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)
    print("✅ 자막 파일(playlist.srt) 생성 완료.")

    with open("audio_concat.txt", "w", encoding="utf-8") as f:
        for _ in range(required_loops):
            for a in existing_audios:
                f.write(f"file '{a}'\n")
            
    merged_audio = "playlist_audio.mp3"
    subprocess.run([
        ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", 
        "-i", "audio_concat.txt", "-c", "copy", merged_audio
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    # 2. 16:9 이미지 생성
    bg_image = generate_playlist_thumbnail()
    if not bg_image:
        print("❌ 배경 이미지가 없어 중단합니다.")
        return
        
    # 3. 비디오 렌더링 (16:9, 중앙 텍스트)
    print("\n[플레이리스트] 영상 렌더링 시작 (16:9, 텍스트 효과 포함)...")
    output_file = "daily_playlist.mp4"
    
    # 15 fps 적용 및 줌팬 속도 감속 조정 (1.0 + it/20000)
    fps = 15
    zoompan_d = int(playlist_total_duration * fps)
    
    filter_complex = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p,"
        f"zoompan=z='1.0+it/20000':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={zoompan_d}:s=1920x1080:fps={fps},"
        "vignette=angle=PI/4[bg]; "
        "[1:a]showfreqs=s=200x80:mode=bar:ascale=log:fscale=log:colors=white@0.9[raw_freqs]; "
        "[raw_freqs]drawgrid=w=12:h=80:t=4:c=black,colorkey=black:0.1:0.0[wave]; "
        "[bg][wave]overlay=(W-w)/2:H-h-120:shortest=1,"
        "noise=alls=12:allf=t+u,eq=brightness='0.005*sin(t*10)':contrast='1.0+0.02*sin(t*15)':saturation=0.8[outv]"
    )
    
    # GPU 가속 코덱 설정 감지
    encoder = get_ffmpeg_encoder(ffmpeg_bin)
    if encoder == "h264_nvenc":
        video_opts = ["-c:v", "h264_nvenc", "-preset", "fast", "-cq", "23"]
    else:
        video_opts = ["-c:v", "libx264", "-preset", "fast", "-crf", "23"]
        
    command = [
        ffmpeg_bin,
        "-i", bg_image,
        "-i", merged_audio,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "1:a",
    ] + video_opts + [
        "-c:a", "aac",
        "-r", str(fps),
        "-t", f"{playlist_total_duration:.2f}",
        "-movflags", "+faststart",
        "-y",
        output_file
    ]
    
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print(f"✅ 플레이리스트 렌더링 완료: {output_file}")
    
    # 4. 유튜브 업로드
    if is_debug:
        print("\nℹ️ [디버그 모드] 유튜브 예약 업로드 단계를 건너뜁니다.")
        return
        
    youtube = get_authenticated_service()
    if youtube:
        now = datetime.now().astimezone()
        date_str = now.strftime("%Y-%m-%d")
        
        # 커뮤니티 소통 유도용 감성 문구 자동 생성 (Gemini)
        community_msg = "오늘 하루는 어떠셨나요? 여러분의 기분을 댓글로 남겨주세요!"
        try:
            print("\n[플레이리스트] 유튜브 설명란 소통 유도 문구(Q&A) 생성 중...")
            client = genai.Client()
            msg_prompt = "유튜브 음악 플레이리스트 설명란 최상단에 들어갈 시청자 소통 유도용 감성적인 인사말과 가벼운 질문(Q&A)을 2문장으로 작성해줘. 여러 옵션을 주지 말고, '여기 문구가 있습니다' 같은 인사말 없이 오직 바로 사용할 수 있는 2문장의 결과물 텍스트만 단일로 출력해."
            msg_response = client.models.generate_content(model="gemini-1.5-flash", contents=msg_prompt)
            if msg_response.text:
                community_msg = msg_response.text.strip()
                print(f"👉 생성된 문구: {community_msg}")
        except Exception as e:
            print(f"⚠️ 소통 문구 생성 실패 (기본 문구 사용): {e}")
        
        title = f"Chill Lofi Study Beats 🌙 | Luna's Daily Lofi Mix ({date_str})"
        
        # 타임스탬프 텍스트 생성
        timestamp_text = "\n[Timestamps]\n"
        current_ts = 0.0
        for loop in range(required_loops):
            for i, duration in enumerate(audio_durations):
                h, m, s = int(current_ts // 3600), int((current_ts % 3600) // 60), int(current_ts % 60)
                if h > 0:
                    ts_str = f"{h}:{m:02d}:{s:02d}"
                else:
                    ts_str = f"{m:02d}:{s:02d}"
                timestamp_text += f"{ts_str} {titles[i]}\n"
                current_ts += duration
                
        description = f"{community_msg}\n\n========================\n\n⚠️ 본 영상의 음악과 이미지는 모두 AI 기술을 활용하여 자동 생성(창작)되었습니다.\n(This video's music and images were created using AI technology.)\n\nAgent Luna가 최신 트렌드를 분석하여 자동 생성한 오늘의 음악들을 하나로 모은 플레이리스트입니다.\n{timestamp_text}\n#playlist #music #vlog #AgentLuna #daily"
        tags = ["playlist", "music", "ai", "daily", "chill", "lofi", "study"]
        
        publish_time = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0).isoformat()
        
        upload_video(youtube, title, description, tags, output_file, publish_time)
        print("✅ 플레이리스트 영상 업로드 완료!")

if __name__ == "__main__":
    create_and_upload_playlist()
