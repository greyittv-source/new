import os
import json
import sys
from google import genai
from google.genai import types

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1]

from pregenerate_daily_playlists import THEMES
from make_shorts import make_shorts

def fix_all_shorts():
    print("🚀 [복구 스크립트] 5일 치 쇼츠 전면 재구축을 시작합니다.")
    client = genai.Client()
    base_dir = "daily_playlists"

    for theme in THEMES:
        theme_dir_name = f"week{theme['day']}_{theme['name'].replace(' ', '_').lower()}"
        theme_dir = os.path.join(base_dir, theme_dir_name)
        
        bg_raw_path = os.path.join(theme_dir, "background_raw.png")
        
        if not os.path.exists(bg_raw_path):
            print(f"\n🎨 [{theme['name']}] 글자가 없는 원본 배경 이미지(background_raw.png) 복구 중...")
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
                    with open(bg_raw_path, "wb") as f:
                        f.write(result.generated_images[0].image.image_bytes)
                    print(f"✅ 원본 배경 이미지 복구 완료: {bg_raw_path}")
            except Exception as e:
                print(f"❌ 이미지 복구 실패: {e}")
                continue
        else:
            print(f"\n🎨 [{theme['name']}] 원본 배경 이미지가 이미 존재합니다. (건너뜀)")
            
        # 재렌더링
        bg_path = os.path.join(theme_dir, "background.png")
        
        # playlist_audio.mp3가 삭제되었으므로 track_1.mp3 사용
        audio_path = os.path.join(theme_dir, "track_1.mp3")
        output_path = os.path.join(theme_dir, f"shorts_day{theme['day']}.mp4")
        
        print(f"🎬 [{theme['name']}] 쇼츠 영상을 재렌더링합니다...")
        try:
            make_shorts(bg_path, audio_path, output_path, theme['title'], theme['description'], ["lofi", "shorts"], is_debug=True)
        except Exception as e:
            print(f"❌ 렌더링 실패: {e}")

    print("\n🎉 모든 쇼츠 재렌더링 완료!")

if __name__ == "__main__":
    fix_all_shorts()
