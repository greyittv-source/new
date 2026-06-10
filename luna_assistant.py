import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

# .env 환경변수 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

import speech_recognition as sr
import google.generativeai as genai
from luna_voice import speak

gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    print("⚠️ GEMINI_API_KEY가 없습니다. 대화 모델을 시작할 수 없습니다.")
    sys.exit(1)

# Gemini 초기화 및 챗봇 세션 생성
genai.configure(api_key=gemini_key)
system_instruction = (
    "당신의 이름은 '루나(Luna)'이며, 대표님(CEO)의 명령을 수행하는 Greyit TV 유튜브 채널의 수석 매니저이자 비서입니다. "
    "당신은 항상 대표님께 깍듯한 존댓말을 사용하며, 밝고 친절하고 똑부러지는 태도를 가집니다. "
    "대표님이 질문하거나 명령하면, 당신은 음성으로 대답하게 됩니다. 따라서 텍스트가 너무 길면 안 됩니다. 1~2문장으로 핵심만 짧고 자연스럽게 대답하세요. "
    "마치 옆에 있는 사람과 대화하듯 편안한 구어체를 사용하고, 읽기 힘든 이모지나 기호(*, # 등)는 절대 사용하지 마세요."
)
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
    chat = model.start_chat(history=[])
except Exception as e:
    print(f"⚠️ 제미나이 모델 초기화 실패: {e}")
    sys.exit(1)

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile

def record_audio_vad(filename="temp_audio.wav", threshold=0.015, silence_duration=1.5, samplerate=16000):
    chunk_duration = 0.1
    chunk_samples = int(samplerate * chunk_duration)
    
    audio_data = []
    silence_frames = 0
    max_silence_frames = int(silence_duration / chunk_duration)
    
    stream = sd.InputStream(samplerate=samplerate, channels=1, dtype='float32')
    with stream:
        # 1. 말하기 시작 대기 (최대 10초)
        start_wait = time.time()
        while True:
            chunk, _ = stream.read(chunk_samples)
            volume = np.sqrt(np.mean(chunk**2))
            if volume > threshold:
                audio_data.append(chunk)
                break
            if time.time() - start_wait > 5:
                return False # 아무 말 안함
                
        # 2. 말하는 중 (조용해질 때까지 녹음)
        while True:
            chunk, _ = stream.read(chunk_samples)
            volume = np.sqrt(np.mean(chunk**2))
            audio_data.append(chunk)
            
            if volume < threshold:
                silence_frames += 1
            else:
                silence_frames = 0
                
            if silence_frames >= max_silence_frames:
                break
                
    recording = np.concatenate(audio_data, axis=0)
    wavfile.write(filename, samplerate, (recording * 32767).astype(np.int16))
    return True

def listen_and_respond():
    recognizer = sr.Recognizer()
    
    print("\n🎙️ [음성 비서 루나] 시스템이 초기화되었습니다.")
    print("✨ 루나가 대표님의 목소리를 기다립니다! ('종료'라고 말씀하시면 꺼집니다)")
    speak("대표님, 말씀하십시오. 듣고 있습니다.")
    
    while True:
        try:
            has_voice = record_audio_vad("temp.wav")
            
            if not has_voice:
                continue # 타임아웃 시 계속 루프
                
            print("⏳ 텍스트로 변환 중...")
            with sr.AudioFile("temp.wav") as source:
                audio = recognizer.record(source)
                
            text = recognizer.recognize_google(audio, language='ko-KR')
            print(f"👤 대표님: {text}")
            
            if "종료" in text or "그만" in text:
                speak("네 대표님, 음성 대화 모드를 종료합니다. 필요하시면 언제든 다시 불러주세요.")
                break
                
            # Gemini에게 질문 전송
            print("🤔 루나가 생각 중...")
            response = chat.send_message(text)
            reply_text = response.text.replace("*", "").replace("#", "")
            
            print(f"🤖 루나: {reply_text}")
            speak(reply_text)
            
        except sr.UnknownValueError:
            pass # 인식 불가 시 조용히 넘어감
        except Exception as e:
            print(f"⚠️ 오류 발생: {e}")
            time.sleep(2)

if __name__ == "__main__":
    listen_and_respond()
