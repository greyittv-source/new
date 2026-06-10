import os
import sys
import random
import datetime
from google import genai
from google.genai import types

# Windows에서 cp949 인코딩 충돌 방지를 위해 stdout을 utf-8로 강제 설정
sys.stdout.reconfigure(encoding='utf-8')

# .env 파일 수동 로드 로직 (python-dotenv 미설치 환경 대비)
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = line.strip().split("=", 1)[1]

# 1. 제미나이 API 클라이언트 연결 (환경 변수 GEMINI_API_KEY 설정 필요)
client = genai.Client()

# 2. 텍스트 모델(Gemini 2.5 Flash)로 트렌드 키워드 추출, 기획안 및 오디오 프롬프트 생성
iteration_idx = sys.argv[1] if len(sys.argv) > 1 else str(random.randint(1, 100))

today = datetime.datetime.now().astimezone()
weekday = today.weekday() # 0: Mon, 1: Tue, ..., 6: Sun

# 요일별 장르 동적 설정
if weekday in [4, 5]: # 금, 토
    target_genre = "Upbeat Synthwave / Chillwave"
elif weekday == 6: # 일
    target_genre = "Relaxing Jazz Hop"
else: # 월~목
    target_genre = "Cinematic Lo-fi"
    
print(f"\n[Step 1] 콘텐츠 기획 및 썸네일 프롬프트 생성 중... (루프: {iteration_idx}, 오늘의 장르: {target_genre})")

trend_data = "트렌드 데이터를 불러올 수 없습니다."
if os.path.exists("daily_trends.txt"):
    with open("daily_trends.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()[:20]
        trend_data = "".join(lines)

spotify_data = ""
if os.path.exists("spotify_trends.txt"):
    with open("spotify_trends.txt", "r", encoding="utf-8") as f:
        spotify_data = f.read()

text_prompt = f"""
당신은 유튜브 음악 채널 자동화 에이전트 루나입니다.
아래의 오늘자 최신 유튜브 뮤직 트렌드(Top 20) 및 스포티파이 인기 Lofi 곡 정보 분석을 바탕으로 분위기를 파악하여, 오늘 업로드할 {iteration_idx}번째 30초 길이의 '{target_genre}' 숏폼 음악 기획안을 작성하세요.

[오늘의 음악 트렌드 데이터]
{trend_data}

[스포티파이 Lofi 인기 곡 정보]
{spotify_data}

**[유튜브 알고리즘 최적화(SEO) 규칙]**
1. 영상의 제목은 무조건 `[아티스트명(가상)] - [곡 제목]` 형태를 유지합니다. (예: `Luna - Neon Dreams`)
2. 리믹스나 무드 강조가 있다면 소괄호를 씁니다. (예: `(Slowed)`, `(Night Drive)`)
3. 영문 단어의 첫 글자는 대문자(Title Case)로 씁니다. 특수문자나 이모티콘은 제목에서 절대 사용하지 마세요.
4. 썸네일 프롬프트 작성 시, 만약 타겟 장르가 'Upbeat Synthwave / Chillwave'라면 반드시 네온사인, 사이버펑크, 레트로 스포츠카, 화려한 야경 등의 시각적 요소를 강하게 포함하여 영문 프롬프트를 작성하세요.
5. 유튜브 해시태그에 들어갈 트렌드 키워드 5개를 추출하여 영상 설명란 하단에 배치하세요.

다음 형식에 맞춰 출력해주세요:
1. 영상의 제목 (SEO 규칙 엄수)
2. 영상 설명 (음악의 분위기와 기획 의도를 투명하게 공개하는 문구) + 트렌드 키워드 해시태그
3. 썸네일 이미지 생성을 위한 프롬프트 영문
4. Lyria 모델에 넣을 영어 음악 생성 프롬프트 (반드시 "A 30-second cinematic lo-fi track..." 등 30초 분량을 명시할 것)
"""

plan_response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents=text_prompt,
)
plan_text = plan_response.text

# 기획안 저장
with open("lyrics_and_plan.txt", "w", encoding="utf-8") as f:
    f.write(plan_text)
print("✅ 기획안(lyrics_and_plan.txt) 추출 완료.")

# 곡 제목(Title) 파싱 및 저장 (자막용)
import re
title_text = f"Luna's Original Track {iteration_idx}"
match = re.search(r'([A-Za-z0-9가-힣\s]+ - [A-Za-z0-9가-힣\s\(\)]+)', plan_text)
if match:
    title_text = match.group(1).replace('`', '').strip()
with open(f"title_{iteration_idx}.txt", "w", encoding="utf-8") as f:
    f.write(title_text)
print(f"🎵 곡 제목 저장 완료: {title_text}")

# 3. Lyria 모델로 오디오 생성 정상화
print("\n[Step 2] Lyria 엔진 가동: AI 오디오(mp3) 생성 중... (결제 연동됨)")
# 기획안에서 추출한 Lyria 프롬프트를 사용할 수 있도록 파싱 (간단히 정규식 사용)
import re
audio_prompt = "A 30-second cinematic lo-fi track with a melancholic and peaceful mood, featuring subtle piano melodies and gentle rain sound effects."
audio_match = re.search(r'(?:4\.\s*Lyria.*?|음악 생성 프롬프트[^\n]*)\n(.*)', plan_text, re.IGNORECASE | re.DOTALL)
if audio_match:
    # 빈 줄을 제외한 첫 번째 텍스트 블록
    lines = [line.strip() for line in audio_match.group(1).strip().split('\n') if line.strip() and not line.startswith('**')]
    if lines:
        audio_prompt = lines[0]
        
print(f"🎵 사용된 프롬프트: {audio_prompt}")

try:
    audio_response = client.models.generate_content(
        model="lyria-3-clip-preview",
        contents=audio_prompt,
    )
    
    audio_bytes = None
    for candidate in audio_response.candidates:
        if not candidate.content:
            print("⚠️ candidate.content가 None입니다. 원인 파악 중...")
            print("Candidate 데이터:", candidate)
            continue
            
        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                audio_bytes = part.inline_data.data
                break
                
    if audio_bytes:
        with open("clip.mp3", "wb") as f:
            f.write(audio_bytes)
        print("✅ 오디오 생성 성공! (clip.mp3 저장 완료)")
    else:
        print("⚠️ 오디오 데이터가 응답에 포함되지 않았습니다.")
        print("전체 응답 원본:", audio_response)

except Exception as e:
    print(f"❌ [Lyria 에러] 결제 연동 후에도 오류가 발생했습니다: {e}")
