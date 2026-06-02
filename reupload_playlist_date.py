import os
import subprocess
from datetime import datetime
import sys
import io
import math
from PIL import Image
from google import genai
from google.genai import types
import moviepy.config as cfg

sys.stdout.reconfigure(encoding='utf-8')

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1]

from upload_youtube import get_authenticated_service

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
            prompt_response = client.models.generate_content(model="gemini-2.5-flash", contents=extract_prompt)
            image_prompt = prompt_response.text.strip()
            print(f"👉 추출된 기본 프롬프트: {image_prompt}")
        except Exception:
            pass

    try:
        result = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=image_prompt + " wide landscape, highly detailed, atmospheric",
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="16:9"
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
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_w = right - left
            text_h = bottom - top
            
            W, H = image.size
            x = (W - text_w) / 2
            y = (H - text_h) / 2
            
            draw.text((x + 5, y + 5), text, font=font, fill=(0, 0, 0, 180))
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 230))

            image.save("playlist_bg_reupload.png", "PNG")
            print("✅ 16:9 썸네일 생성 완료 (playlist_bg_reupload.png)")
            return "playlist_bg_reupload.png"
    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")
    return None

def upload_video_public(youtube, title, description, tags, file_path):
    from googleapiclient.http import MediaFileUpload
    print(f"\n🎬 유튜브 업로드 시작...\n - 제목: {title}\n - 파일: {file_path}")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '10'  # Music
        },
        'status': {
            'privacyStatus': 'public',  # 공개 업로드
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    print("⏳ 동영상을 유튜브 서버로 전송 중입니다...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"진행률: {int(status.progress() * 100)}%")
            
    print(f"✅ 성공! 비디오 업로드 완료 (공개 상태)")
    print(f"🔗 확인 링크: https://studio.youtube.com/video/{response['id']}/edit")
    return response['id']

def reupload_playlist_for_date(target_date):
    print(f"\n🎬 [{target_date} 플레이리스트 복구] 영상을 생성 및 업로드합니다...")
    
    audios = [f"audio_{i}.mp3" for i in range(1, 4)]
    existing_audios = [a for a in audios if os.path.exists(a)]
    
    if not existing_audios:
        print("❌ 연결할 오디오 파일이 없습니다.")
        return
        
    ffmpeg_bin = cfg.get_setting("FFMPEG_BINARY")
    
    print("\n[플레이리스트] 오디오 길이 계산 및 병합 중...")
    from moviepy.editor import AudioFileClip
    
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
            
    required_loops = 1
    if total_original_duration > 0 and total_original_duration < 180:
        required_loops = math.ceil(180 / total_original_duration)
        print(f"👉 반복 횟수: {required_loops}회")

    # 자막 생성
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
            end_sec = current_time + 8.0
            if end_sec > current_time + duration:
                end_sec = current_time + duration
                
            srt_content += f"{srt_index}\n"
            srt_content += f"{format_srt_time(start_sec)} --> {format_srt_time(end_sec)}\n"
            srt_content += f"🎵 Now Playing: {titles[i]}\n\n"
            
            srt_index += 1
            current_time += duration

    with open("playlist_reupload.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)

    with open("audio_concat_reupload.txt", "w", encoding="utf-8") as f:
        for _ in range(required_loops):
            for a in existing_audios:
                f.write(f"file '{a}'\n")
            
    merged_audio = "playlist_audio_reupload.mp3"
    subprocess.run([
        ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", 
        "-i", "audio_concat_reupload.txt", "-c", "copy", merged_audio
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    bg_image = generate_playlist_thumbnail()
    if not bg_image:
        print("❌ 배경 이미지가 없습니다.")
        return
        
    print("\n[플레이리스트] 영상 렌더링 중...")
    output_file = "playlist_reupload.mp4"
    
    filter_complex = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p,"
        f"zoompan=z='1.0+it/10000':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(current_time * 30) + 100}:s=1920x1080:fps=30,"
        "vignette=angle=PI/4[bg]; "
        "[1:a]showfreqs=s=200x80:mode=bar:ascale=log:fscale=log:colors=white@0.9[raw_freqs]; "
        "[raw_freqs]drawgrid=w=12:h=80:t=4:c=black,colorkey=black:0.1:0.0[wave]; "
        "[bg][wave]overlay=(W-w)/2:H-h-120:shortest=1,"
        "noise=alls=8:allf=t+u,eq=saturation=0.8:contrast=1.1[outv]"
    )
    
    command = [
        ffmpeg_bin,
        "-i", bg_image,
        "-i", merged_audio,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-t", f"{current_time:.2f}",
        "-movflags", "+faststart",
        "-y",
        output_file
    ]
    
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print(f"✅ 플레이리스트 렌더링 완료: {output_file}")
    
    youtube = get_authenticated_service()
    if youtube:
        community_msg = "지친 마음을 감싸 안아줄 음악들이 이곳에 모여 있어요."
        try:
            client = genai.Client()
            msg_prompt = "유튜브 음악 플레이리스트 설명란 최상단에 들어갈 시청자 소통 유도용 감성적인 인사말과 가벼운 질문(Q&A)을 2문장으로 작성해줘. 오직 2문장의 결과물 텍스트만 단일로 출력해."
            msg_response = client.models.generate_content(model="gemini-2.5-flash", contents=msg_prompt)
            if msg_response.text:
                community_msg = msg_response.text.strip()
        except Exception:
            pass
        
        title = f"Luna's Daily Vibes Mix 🎵 ({target_date})"
        
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
        tags = ["playlist", "music", "ai", "daily", "chill", "vibes"]
        
        upload_video_public(youtube, title, description, tags, output_file)
        print(f"✅ [{target_date}] 플레이리스트 영상 재업로드 완료!")

if __name__ == "__main__":
    reupload_playlist_for_date("2026-05-30")
