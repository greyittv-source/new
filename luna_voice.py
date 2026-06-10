import asyncio
import edge_tts
import pygame
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# MS Azure 고품질 한국어 여성 음성
VOICE = "ko-KR-SunHiNeural"
OUTPUT_FILE = "luna_speech.mp3"

async def _generate_audio(text):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(OUTPUT_FILE)

def speak(text):
    print(f"🎙️ [Luna] {text}")
    try:
        # 1. 텍스트를 MP3로 변환
        asyncio.run(_generate_audio(text))
        
        # 2. Pygame으로 MP3 재생
        pygame.mixer.init()
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()
        
        # 3. 재생이 끝날 때까지 대기
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        # 4. 파일 핸들 해제
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
    except Exception as e:
        print(f"⚠️ [음성 재생 실패] {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        speak(sys.argv[1])
    else:
        speak("안녕하세요 대표님! 수석 매니저 루나입니다. 이제 제 목소리가 잘 들리시나요?")
