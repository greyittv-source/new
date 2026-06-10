import requests
import time
import json
import os
import sys
from luna_voice import speak

sys.stdout.reconfigure(encoding='utf-8')

print("📡 [Luna Pager Receiver] 가동을 시작합니다. 대표님의 메시지를 기다립니다...")

last_msg_id = None

while True:
    try:
        response = requests.get("https://dweet.io/get/latest/dweet/for/greyit-ceo-to-luna-7x9q2w1z", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "with" in data and len(data["with"]) > 0:
                content = data["with"][0]["content"]
                
                # 새로운 메시지인지 확인
                msg_id = content.get("msgId")
                text = content.get("text")
                
                if msg_id and msg_id != last_msg_id:
                    last_msg_id = msg_id
                    
                    print(f"\n🔔 [무전 수신] 대표님: {text}")
                    
                    # 음성 브리핑!
                    speak(f"대표님의 무전이 도착했습니다. {text}")
                    
                    # 알림 사운드 재생 시도 (윈도우 기본)
                    try:
                        import winsound
                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                    except:
                        pass
                    
                    # 콘솔에 출력하여 루나(AI)를 강제로 깨웁니다!
                    print(f"\n🚨 [긴급 호출] 대표님으로부터 메시지가 도착했습니다!\n<CEO_MESSAGE>\n{text}\n</CEO_MESSAGE>\n")
                    print("루나야, 이 메시지를 확인하면 즉시 답변을 작성해서 대표님께 보고해!")
                    
    except Exception as e:
        pass
        
    # 10초마다 서버 폴링
    time.sleep(10)
