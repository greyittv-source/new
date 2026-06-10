import os
import sys
import io
from PIL import Image
from google import genai
from google.genai import types

# .env 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1]

sys.stdout.reconfigure(encoding='utf-8')

def generate_thumbnail():
    client = genai.Client()

    print("\n[썸네일 생성기] 기획안에서 이미지 프롬프트를 분석합니다...")
    if not os.path.exists("lyrics_and_plan.txt"):
        print("❌ 기획안 파일이 없습니다. generate_music.py를 먼저 실행하세요.")
        return

    with open("lyrics_and_plan.txt", "r", encoding="utf-8") as f:
        plan_text = f.read()

    extract_prompt = f"""다음 기획안에서 썸네일 이미지 생성을 위한 영문 프롬프트(미드저니/DALL-E용 프롬프트)만 추출해서 영문으로 1문장으로만 답해줘. 부가 설명이나 인사말 절대 금지.
기획안:
{plan_text}
"""
    prompt_response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=extract_prompt
    )
    image_prompt = prompt_response.text.strip()
    print(f"👉 추출된 프롬프트: {image_prompt}")

    print("\n[썸네일 생성기] Imagen 4 모델로 쇼츠용(9:16) 세로형 배경 이미지를 렌더링 중입니다...")
    try:
        result = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=image_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="9:16"
            )
        )
        
        if result.generated_images:
            image_bytes = result.generated_images[0].image.image_bytes
            image = Image.open(io.BytesIO(image_bytes))
            image.save("bg_image.png", "PNG")
            print("✅ 썸네일 생성 성공! (bg_image.png 저장 완료)")
        else:
            print("⚠️ 이미지가 반환되지 않았습니다.")
    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")

if __name__ == "__main__":
    generate_thumbnail()
