import os
import sys
import shutil
import time
import json
import math
import subprocess
from datetime import datetime, timedelta
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

# 5가지 감성 테마 설정
THEMES = [
    {
        "day": 1,
        "name": "Cozy Rain Cafe",
        "music_prompt": "A cozy lo-fi hip hop track with soft melancholic piano chords, gentle rain tapping on a window, and warm ambient coffee shop atmosphere.",
        "image_prompt": "A cozy window-side seat in a coffee shop, rainy day, soft warm lighting, a hot cup of coffee with steam on the table, a sleeping cat curled up on a chair, aesthetic lofi artwork, 16:9 aspect ratio.",
        "sub_text": "Rainy Cafe Lofi Beats 🌧️",
        "title": "비 오는 날 당신의 감정을 다독여줄 조용한 카페 🌧️ | 번아웃 수면 유도 Lofi",
        "description": "On days when your head is heavy with complex thoughts, sit by the window of a rainy cafe and let your mind rest to the sound of rain and piano melodies. Your day was absolutely wonderful.\n-\n복잡한 생각들로 머리가 무거운 날, 비 오는 카페 창가 자리에 앉아 빗소리와 피아노 선율에 마음을 내려놓으세요. 당신의 하루는 충분히 훌륭했습니다.",
        "pinned_comment": "오늘 하루도 정말 고생 많으셨습니다. 지금 어떤 고민 때문에 밤을 지새우고 계시나요? 이곳에 편하게 털어놓고 가벼운 마음으로 잠드셨으면 좋겠습니다."
    },
    {
        "day": 2,
        "name": "Midnight Library",
        "music_prompt": "A mellow lo-fi study track featuring a slow acoustic nylon guitar melody, soft vinyl crackles, and quiet pages turning sounds.",
        "image_prompt": "A quiet vintage library at midnight, warm desk lamp illuminating open books, cozy leather armchair, a small glowing neon sign saying 'Greyit', soft glowing bokeh, aesthetic lofi artwork, 16:9 aspect ratio.",
        "sub_text": "Midnight Study Lofi 🌙",
        "title": "모두가 잠든 새벽 3시, 생각에 잠겨 듣는 도서관 Lofi 🌙 | 불면증, 공부 집중",
        "description": "In the quiet midnight library with no one around, this dreamy lofi beat is perfect to listen to while turning the pages under the soft desk lamp.\n-\n아무도 없는 고요한 심야의 도서관, 은은한 스탠드 조명 아래서 책장을 넘기며 듣기 좋은 몽환적인 감성 Lofi 비트입니다.",
        "pinned_comment": "새벽에 깨어계시는군요. 지금 어떤 공부를 하고 계시거나, 어떤 상상을 하고 계시나요? 당신의 꿈을 응원합니다. 🌙"
    },
    {
        "day": 3,
        "name": "Sunny Bedroom",
        "music_prompt": "An upbeat and heartwarming lo-fi track with a sunny electric piano riff, birds chirping softly, and a relaxed bedroom groove.",
        "image_prompt": "A bright cozy bedroom on a sunny Sunday morning, warm golden sunlight rays streaming through a large window, a small glowing neon sign saying 'Greyit' on the wall, aesthetic green house plants, pastel colors, 16:9 aspect ratio.",
        "sub_text": "Sunny Sunday Lofi ☕",
        "title": "지친 몸을 일으켜줄 따뜻한 일요일 아침 햇살 ☕ | 우울함 타파 기분전환 Lofi",
        "description": "On mornings when it's hard to get out of bed, this warm lofi music with pleasant piano melodies and birdsong will breathe a little energy into your day.\n-\n이불 밖으로 나오기 힘든 아침, 기분 좋은 피아노 선율과 새소리로 당신의 하루에 작은 활력을 불어넣어 줄 따뜻한 Lofi 음악입니다.",
        "pinned_comment": "기분 좋은 아침, 혹은 느긋한 오후입니다. 오늘 하루 나를 위해 해주고 싶은 작은 선물이 있다면 무엇인가요? ☕"
    },
    {
        "day": 4,
        "name": "Forest Log Cabin",
        "music_prompt": "A warm and peaceful lo-fi track with acoustic guitar strums, the comforting sound of a crackling fireplace, and cozy winter wind outside.",
        "image_prompt": "A cozy wooden log cabin interior, a stone fireplace with a bright crackling fire, comfortable armchairs, a sleeping cat on the rug, a window showing a snowy pine forest, 16:9 aspect ratio.",
        "sub_text": "Cabin Fireplace Lofi 🔥",
        "title": "복잡한 세상과 단절된 숲속 오두막 화로 앞 🔥 | 극도의 아늑함, 불안감 해소",
        "description": "In the deep snowy forest, gently melt your frozen heart relying on the sound of a crackling campfire and warm acoustic guitar melodies.\n-\n눈 내리는 깊은 숲속, 모닥불 타는 소리와 따뜻한 어쿠스틱 기타 선율에 의지해 얼어붙은 마음을 사르르 녹여보세요.",
        "pinned_comment": "세상과 잠시 단절된 느낌이 들 때가 있죠. 가장 돌아가고 싶은 따뜻한 기억 한 조각을 이곳에 꺼내놓아 보세요. 🔥"
    },
    {
        "day": 5,
        "name": "Vintage Train Ride",
        "music_prompt": "A dreamy, spacey lo-fi synthwave track with a gentle train track clacking sound, soft pads, and a nostalgic wandering melody.",
        "image_prompt": "Inside a vintage train passenger carriage at night, looking out of the window at city lights reflecting in the rain, a small glowing neon sign saying 'Greyit' in the cabin, nostalgic lofi anime style, 16:9 aspect ratio.",
        "sub_text": "Night Train Journey 🌌",
        "title": "창밖으로 스쳐 가는 야경과 후회들을 털어내는 밤기차 🌌 | 노스탤지어 감성 Lofi",
        "description": "Leaning against the window of a night train with no destination, this dreamy music is perfect for brushing off your lingering regrets along with the dark night view.\n-\n목적지 없는 밤기차 창가에 기대어, 어두운 야경과 함께 마음속의 미련들을 훌훌 털어내기 좋은 몽환적인 감성의 음악입니다.",
        "pinned_comment": "우리는 어디로 달려가고 있는 걸까요? 이 기차가 당신을 가장 가고 싶은 곳으로 데려다준다면, 어디로 가고 싶나요? 🌌"
    },
    {
        "day": 6,
        "name": "Peaceful Morning Calm",
        "music_prompt": "A peaceful and tranquil lo-fi track with soft acoustic guitar, gentle piano melodies, and the faint sound of morning birds in a quiet traditional temple.",
        "image_prompt": "A quiet and peaceful traditional Korean temple in the early morning, soft mist rolling over the mountains, warm sunrise lighting, a cute fluffy cat sitting on the stone stairs, aesthetic lofi artwork, 16:9 aspect ratio.",
        "sub_text": "Morning Calm Lofi 🕊️",
        "title": "마음이 무너질 때 위로가 되어주는 아침 산사의 고요함 🕊️ | 번아웃, 명상 Lofi",
        "description": "Leave the complex world for a moment and lay down your burdens in the tranquility of a morning mountain temple. This beat contains peace and a moment of silence for the fallen heroes.\n-\n복잡한 세상을 잠시 떠나 아침 산사의 고요함 속에 마음의 짐을 내려놓으세요. 호국보훈의 달, 순국선열을 향한 묵념과 평화를 담은 비트입니다.",
        "pinned_comment": "가끔은 다 내려놓고 쉬어가도 괜찮습니다. 지금 당신의 마음을 가장 무겁게 짓누르는 걱정은 무엇인가요? 🕊️ (당신의 지친 마음이 언제든 쉬어갈 수 있도록, 구독과 좋아요, 알림 설정으로 함께해 주세요.)"
    },
    {
        "day": 7,
        "name": "Silent Memorial Park",
        "music_prompt": "A solemn and melancholic lo-fi track with slow emotional string swells, warm vinyl crackles, and a respectful quiet atmosphere.",
        "image_prompt": "A peaceful memorial park with lush green trees, sunlight filtering through the leaves, a quiet wooden bench, a glowing neon sign saying 'Greyit' softly hidden in the grass, aesthetic lofi style, 16:9 aspect ratio.",
        "sub_text": "Silent Memorial Lofi 🌿",
        "title": "누군가를 그리워하며 걷는 평화로운 공원 🌿 | 숭고한 휴식, 눈물샘 자극",
        "description": "A warm and melancholic lofi piano melody that soothes the empty heart longing for someone out of reach.\n-\n닿을 수 없는 사람을 그리워하는 헛헛한 마음을 달래주는 따뜻하고 먹먹한 감성의 Lofi 피아노 선율입니다.",
        "pinned_comment": "문득 누군가가 사무치게 그리워지는 날이 있습니다. 오늘, 가장 먼저 떠오른 사람은 누구인가요? 🌿 (이 따뜻한 위로가 계속될 수 있도록, 구독과 좋아요, 알림 설정으로 Greyit TV와 함께해 주세요.)"
    },
    {
        "day": 8,
        "name": "Historical Heritage",
        "music_prompt": "A unique lo-fi hip hop fusion track featuring traditional Asian instruments like gayageum, subtle lo-fi drum beats, and a peaceful historical vibe.",
        "image_prompt": "An aesthetic view of a traditional Korean Hanok courtyard on a peaceful sunny afternoon, old stone walls, a sleeping cat on the wooden floor, beautiful historical architecture, lofi anime style, 16:9 aspect ratio.",
        "sub_text": "Historical Lofi Vibe 🏯",
        "title": "고궁 돌담길을 거닐며 느끼는 여유로움 🏯 | 한국적 Lofi 퓨전, 마음 정화",
        "description": "The peace of sitting on the wooden floor of an old Hanok bathed in the afternoon sun. An aesthetic oriental lofi mixing gayageum melodies with dreamy beats.\n-\n옛 한옥 마루에 앉아 오후의 햇살을 받는 듯한 평화로움. 가야금 선율과 몽환적인 비트가 섞인 감각적인 동양풍 Lofi입니다.",
        "pinned_comment": "숨가쁘게 돌아가는 현대 사회 속에서, 당신이 가장 평화로움을 느끼는 나만의 안식처는 어디인가요? 🏯 (Greyit TV가 당신만의 안식처가 될 수 있도록, 구독과 좋아요, 알림 설정으로 함께해 주세요.)"
    },
    {
        "day": 9,
        "name": "Eternal Starry Night",
        "music_prompt": "A dreamy, atmospheric lo-fi track with spacious ambient synths, slow rhythmic beats, and emotional piano melodies reflecting on eternal memories.",
        "image_prompt": "A quiet grassy hill at night under a breathtaking starry sky, a gentle breeze, a small glowing neon sign saying 'Greyit' in the foreground, nostalgic and eternal mood, 16:9 aspect ratio.",
        "sub_text": "Eternal Night Lofi ✨",
        "title": "당신의 모든 슬픔을 안아줄 끝없는 밤하늘 ✨ | 우울증 완화, 숙면 테라피",
        "description": "Under the pouring starlight, let all the scars and sorrows accumulated today flow into the universe. You are not alone.\n-\n쏟아지는 별빛 아래, 오늘 하루 쌓였던 모든 상처와 슬픔을 우주로 흘려보내세요. 당신은 혼자가 아닙니다.",
        "pinned_comment": "끝없이 펼쳐진 별빛 아래에 서 있다면, 지금 스스로에게 어떤 위로의 말을 건네고 싶으신가요? ✨ (더 많은 위로와 평안을 전해드릴 수 있도록, 구독과 좋아요, 알림 설정으로 Greyit TV와 함께해 주세요.)"
    }
]

def get_ffmpeg_encoder(ffmpeg_bin):
    """NVIDIA GPU 가속(h264_nvenc)이 실제 작동 가능한지 0.1초 프로브 테스트로 자동 감지합니다."""
    try:
        import subprocess
        probe_file = "test_gpu_probe.mp4"
        test_cmd = [
            ffmpeg_bin, "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64",
            "-t", "0.1", "-c:v", "h264_nvenc", probe_file
        ]
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            if os.path.exists(probe_file):
                try: os.remove(probe_file)
                except Exception: pass
            return "h264_nvenc"
    except Exception:
        pass
    return "libx264"

def generate_daily_assets(client, theme, output_dir, is_debug):
    print(f"\n🎨 [{theme['name']}] 썸네일 이미지 생성 중...")
    bg_path = os.path.join(output_dir, "background.png")
    
    # 1. Imagen 4로 배경 이미지 생성
    try:
        result = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=theme['image_prompt'] + " high resolution, beautiful warm atmosphere, detailed, cinematic composition",
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="16:9"
            )
        )
        if result.generated_images:
            from PIL import Image, ImageDraw, ImageFont
            import io
            image_bytes = result.generated_images[0].image.image_bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # 쇼츠용 원본 배경(글자 없는 상태) 먼저 저장
            bg_raw_path = os.path.join(output_dir, "background_raw.png")
            image.save(bg_raw_path, "PNG")
            
            # 플레이리스트 텍스트 삽입
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
            
            draw.text((x + 5, y + 5), text, font=font, fill=(0, 0, 0, 160)) # 그림자
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 220)) # 메인 텍스트
            
            image.save(bg_path, "PNG")
            print(f"✅ 배경 이미지 생성 완료: {bg_path}")
    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}. 기본 색상 배경으로 대체합니다.")
        from PIL import Image
        img = Image.new('RGB', (1920, 1080), color=(30, 30, 40))
        img.save(bg_path)

    # 2. 오디오 생성 (Lyria API를 순차 호출해 테마별 10곡의 조각 생성)
    audio_paths = []
    num_audios = 3 if is_debug else 10  # 디버그 모드 시 3곡만 생성
    print(f"🎵 오디오 음원 생성 중 ({num_audios}곡)...")
    
    for i in range(1, num_audios + 1):
        audio_filename = f"track_{i}.mp3"
        audio_path = os.path.join(output_dir, audio_filename)
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
            print(f"   [-] ({i}/{num_audios}) 기존 음원 발견: {audio_filename} (Lyria 생성 건너뜀)")
            audio_paths.append(audio_path)
            continue
            
        # 기획 다양성을 위해 프롬프트에 약간의 난수 무드 추가
        variations = ["melancholic", "peaceful", "dreamy", "gentle", "warm"]
        selected_mood = variations[i % len(variations)]
        prompt = f"A 30-second lo-fi track with a {selected_mood} mood. {theme['music_prompt']}"
        
        try:
            print(f"   [-] ({i}/{num_audios}) Lyria 음악 클립 생성 중...")
            audio_response = client.models.generate_content(
                model="lyria-3-clip-preview",
                contents=prompt
            )
            audio_bytes = None
            for candidate in audio_response.candidates:
                if candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            audio_bytes = part.inline_data.data
                            break
                            
            if audio_bytes:
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
                audio_paths.append(audio_path)
                print(f"   ✅ 생성 성공: track_{i}.mp3")
            else:
                print(f"   ⚠️ 오디오 데이터 누락. 더미 파일로 대체합니다.")
                try:
                    subprocess.run(["python", "generate_music.py", str(i)], check=True, timeout=180)
                    if os.path.exists("clip.mp3"):
                        os.rename("clip.mp3", audio_path)
                except subprocess.TimeoutExpired:
                    print(f"   [!] 음원 생성 타임아웃 (180초 초과). 다음 번에 재시도합니다.")
                except Exception as e:
                    print(f"   [!] 음원 생성 오류: {e}. 더미 오디오 대체 적용.")
                if not os.path.exists(audio_path):
                    if os.path.exists("dummy_audio.mp3"):
                        shutil.copy("dummy_audio.mp3", audio_path)
                    else:
                        with open(audio_path, "wb") as f:
                            f.write(b'\x00' * 1000)
                audio_paths.append(audio_path)
        except Exception as e:
            print(f"   ❌ 음원 {i} 생성 에러: {e}. 더미 오디오 대체 적용.")
            if os.path.exists("dummy_audio.mp3"):
                shutil.copy("dummy_audio.mp3", audio_path)
            else:
                with open(audio_path, "wb") as f:
                    f.write(b'\x00' * 1000)
            audio_paths.append(audio_path)
        time.sleep(2) # API 호출 제한 방지
        
    return bg_path, audio_paths

def pregenerate_all_playlists():
    is_debug = "debug" in sys.argv
    print(f"\n🚀 [일간 플레이리스트 선행 빌더] 5일 분량 자동 생성 엔진을 개시합니다. (모드: {'디버그' if is_debug else '정식'})")
    
    client = genai.Client()
    ffmpeg_bin = cfg.get_setting("FFMPEG_BINARY")
    
    # 1. 출력 디렉터리 준비
    base_output_dir = "daily_playlists"
    os.makedirs(base_output_dir, exist_ok=True)
    
    metadata_list = []
    
    for theme in THEMES:
        theme_dir = os.path.join(base_output_dir, f"Day{theme['day']}_{theme['name'].replace(' ', '_').lower()}")
        os.makedirs(theme_dir, exist_ok=True)
        
        print(f"\n==================================================")
        print(f"📦 [Week {theme['day']}] 테마: {theme['name']} 제작 개시")
        print(f"==================================================")
        
        # 1단계: 자산 생성 (배경 및 음원)
        bg_image, audio_paths = generate_daily_assets(client, theme, theme_dir, is_debug)
        
        # 2단계: 오디오 병합
        print("\n[플레이리스트] 오디오 병합 리스트 생성 및 접합 중...")
        from moviepy.editor import AudioFileClip
        
        total_original_duration = 0
        audio_durations = []
        faded_audio_paths = []
        for a in audio_paths:
            try:
                with AudioFileClip(a) as clip:
                    dur = clip.duration
                faded_a = a.replace(".mp3", "_faded.mp3")
                if not os.path.exists(faded_a) or os.path.getsize(faded_a) < 1000:
                    subprocess.run([ffmpeg_bin, "-y", "-i", a, "-af", f"afade=t=in:st=0:d=1.5,afade=t=out:st={dur-1.5:.2f}:d=1.5", faded_a], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                faded_audio_paths.append(faded_a)
                audio_durations.append(dur)
                total_original_duration += dur
            except Exception as e:
                print(f"⚠️ 오디오 페이드 처리 실패: {e}")
                faded_audio_paths.append(a)
                audio_durations.append(30.0)
                total_original_duration += 30.0
                
        target_duration = 300.0 if is_debug else 3600.0
        required_loops = math.ceil(target_duration / total_original_duration)
        playlist_total_duration = total_original_duration * required_loops
        
        # 자막(SRT) 생성
        srt_path = os.path.join(theme_dir, "playlist.srt")
        srt_content = ""
        current_time = 0.0
        srt_index = 1
        
        def format_srt_time(seconds):
            h, m, s = int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
            
        for loop in range(required_loops):
            for i, duration in enumerate(audio_durations):
                start_sec = current_time
                end_sec = current_time + 8.0
                if end_sec > current_time + duration:
                    end_sec = current_time + duration
                    
                srt_content += f"{srt_index}\n"
                srt_content += f"{format_srt_time(start_sec)} --> {format_srt_time(end_sec)}\n"
                srt_content += f"🎵 Now Playing: Track {i+1} ({theme['sub_text']})\n\n"
                
                srt_index += 1
                current_time += duration
                
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
            
        # 오디오 병합 텍스트 파일 작성
        concat_txt_path = os.path.join(theme_dir, "audio_concat.txt")
        with open(concat_txt_path, "w", encoding="utf-8") as f:
            for _ in range(required_loops):
                for a in faded_audio_paths:
                    # 상대 경로로 작성
                    f.write(f"file '{os.path.basename(a)}'\n")
                    
        merged_audio = os.path.join(theme_dir, "playlist_audio.mp3")
        
        # FFmpeg을 활용한 오디오 1차 병합
        subprocess.run([
            ffmpeg_bin, "-y", "-f", "concat", "-safe", "0",
            "-i", concat_txt_path, "-c", "copy", merged_audio
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        # 3단계: 최종 비디오 렌더링
        output_video_path = os.path.join(theme_dir, f"daily_playlist_day{theme['day']}.mp4")
        print(f"\n🎬 16:9 비디오 렌더링 시작 (FHD, 15fps, 이펙트 적용)...")
        
        fps = 15
        zoompan_d = int(playlist_total_duration * fps)
        
        # 자막 경로 백슬래시 처리 (FFmpeg subtitles 필터용 이스케이프)
        srt_filter_path = srt_path.replace("\\", "/").replace(":", "\\:")
        
        filter_complex = (
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p,"
            f"zoompan=z='1.0+it/20000':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={zoompan_d}:s=1920x1080:fps={fps},"
            f"vignette=angle=PI/4[bg]; "
            f"[1:a]showfreqs=s=200x80:mode=bar:ascale=log:fscale=log:colors=white@0.9[raw_freqs]; "
            f"[raw_freqs]drawgrid=w=12:h=80:t=4:c=black,colorkey=black:0.1:0.0[wave]; "
            f"[bg][wave]overlay=(W-w)/2:H-h-120:shortest=1,"
            f"noise=alls=12:allf=t+u,eq=brightness='0.005*sin(t*10)':contrast='1.0+0.02*sin(t*15)':saturation=0.8,"
            f"drawgrid=w=iw:h=4:t=1:c=black@0.1,"
            f"chromashift=cbh=-2:crh=2[outv]"
        )
        
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
            output_video_path
        ]
        
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(f"✅ 렌더링 완료: {output_video_path}")
        
        try:
            if os.name == 'nt':
                os.startfile(output_video_path)
        except Exception:
            pass
        
        # 쇼츠 자동 렌더링 (예고편)
        shorts_output_path = os.path.join(theme_dir, f"shorts_day{theme['day']}.mp4")
        try:
            from make_shorts import make_shorts
            # 쇼츠는 유튜브 업로드를 나중에 따로 하거나 예약할 수 있도록 일단 파일만 렌더링 (is_debug=True)
            make_shorts(bg_image, merged_audio, shorts_output_path, theme['title'], theme['description'], ["lofi", "shorts"], is_debug=True)
            
            # SNS 업로드용 복붙 텍스트 파일 생성
            sns_text_path = os.path.join(theme_dir, f"sns_description_day{theme['day']}.txt")
            sns_content = f"{theme['description']}\n\n💡 Follow and save for daily healing vibes ✨\n(더 많은 힐링 음악을 원하신다면 팔로우와 저장을 꾹 눌러주세요 🎧)\n\n⚠️ The music and images in this video were fully generated using AI technology.\n(본 영상의 음악과 이미지는 모두 AI 기술을 활용하여 창작되었습니다.)\n\n#Shorts #Lofi #StudyMusic #ChillVibes #GreyitTV"
            with open(sns_text_path, "w", encoding="utf-8") as f:
                f.write(sns_content)
            print(f"📝 SNS 복붙용 텍스트 저장 완료: {sns_text_path}")
            
            # 레딧 소프트 프로모션 봇 가동
            try:
                from reddit_bot import post_video_to_reddit
                reddit_title = f"{theme['title']} - {theme['description'][:50]}..."
                reddit_comment = f"Here is the full 1-hour lofi mix on YouTube: https://youtu.be/YOUR_CHANNEL_LINK\n\n#lofi #chill #study"
                target_subs = ["LofiHipHop", "StudyMusic", "chillhop", "aiArt", "Music"]
                target_sub = target_subs[theme['day'] % len(target_subs)]
                
                post_video_to_reddit(
                    title=reddit_title,
                    video_path=shorts_output_path,
                    thumbnail_path=bg_image,
                    comment_text=reddit_comment,
                    subreddit_name=target_sub
                )
            except Exception as e:
                print(f"⚠️ [레딧 업로드 스킵] {e}")
                
            # 인스타그램 릴스 봇 가동
            try:
                from insta_bot import post_reels_to_instagram
                insta_caption = f"{theme['description']}\n\n#lofi #chill #study #GreyitTV"
                post_reels_to_instagram(shorts_output_path, insta_caption)
            except Exception as e:
                print(f"⚠️ [인스타 업로드 스킵] {e}")
                
            # 틱톡 봇 가동
            try:
                from tiktok_bot import post_video_to_tiktok
                tiktok_desc = f"{theme['description']} #lofi #chill"
                post_video_to_tiktok(shorts_output_path, tiktok_desc)
            except Exception as e:
                print(f"⚠️ [틱톡 업로드 스킵] {e}")
            
        except Exception as e:
            print(f"❌ 주간 테마 쇼츠 생성 오류: {e}")
            
        # 메타데이터 정보 보관
        suggested_date = datetime.now() + timedelta(days=7 * theme['day'])
        
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
                timestamp_text += f"{ts_str} Track {i+1} ({theme['sub_text']})\n"
                current_ts += duration
                
        metadata_list.append({
            "day": theme['day'],
            "theme_name": theme['name'],
            "video_file": output_video_path,
            "suggested_upload_date": suggested_date.strftime("%Y-%m-%d 08:00 KST"),
            "pinned_comment": theme.get("pinned_comment", ""),
            "youtube_title": theme['title'],
            "youtube_description": theme['description'] + f"\n\n---\n🌙 Grey it = Great\n머리가 희끗희끗해지는 고난과 아픔 속에서도, 당신의 인생은 여전히 거대하고 위대합니다.\nGreyit TV는 아프고 외로운 사람들이 잠시 머물며 위로를 받을 수 있는 따뜻한 쉼터가 되기를 바랍니다.\n---\n\n⚠️ 본 영상의 음악과 이미지는 모두 AI 기술을 활용하여 자동 생성(창작)되었습니다.\n(This video's music and images were created using AI technology.)\n{timestamp_text}\n#lofi #playlist #chill #study #music #GreyitTV",
            "youtube_tags": ["lofi", "music", "playlist", "study", "relax", "ai"]
        })
        
        # 작업 임시 파일 클리닝
        for temp_file in [concat_txt_path, merged_audio]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    # 4단계: 메타데이터 가이드 파일 저장
    meta_guide_path = os.path.join(base_output_dir, "daily_playlists_metadata.json")
    with open(meta_guide_path, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=4)
        
    print(f"\n🎉 [성공] 5일 분량 플레이리스트 비디오 선행 빌드가 모두 완료되었습니다!")
    print(f"📂 결과물 저장 경로: C:\\Users\\greyi\\biz\\greyittv\\음악채널\\{base_output_dir}")
    print(f"📋 주간 가이드 메타데이터 파일 생성 완료: {meta_guide_path}")

if __name__ == "__main__":
    pregenerate_all_playlists()
