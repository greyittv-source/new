import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def extract_tiktok_session():
    print("\n🌐 [틱톡 세션 추출기] 브라우저를 엽니다. 창이 뜨면 직접 틱톡에 '로그인'해 주세요!")
    print(" (로그인만 완료하시면 제가 쿠키를 훔쳐서 자동으로 .env에 저장하고 닫겠습니다 😎)\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.tiktok.com/")
        
        print("⏳ 로그인이 완료될 때까지 감시 중입니다...")
        
        while True:
            # 브라우저 쿠키 목록 가져오기
            cookies = context.cookies()
            
            # 'sessionid'라는 이름의 쿠키 찾기 (틱톡은 sessionid 쿠키 사용)
            sessionid = next((c['value'] for c in cookies if c['name'] == 'sessionid'), None)
            
            if sessionid and len(sessionid) > 10:
                print(f"\n🎉 빙고! 틱톡 sessionid 쿠키를 획득했습니다: {sessionid[:10]}... (보안상 앞부분만 출력)")
                
                # .env 파일 읽기 및 수정 (기존 TIKTOK_SESSION_ID 항목 덮어쓰기)
                env_path = ".env"
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                else:
                    lines = []
                    
                new_lines = []
                found = False
                for line in lines:
                    if line.startswith("TIKTOK_SESSION_ID="):
                        new_lines.append(f"TIKTOK_SESSION_ID={sessionid}\n")
                        found = True
                    else:
                        new_lines.append(line)
                        
                if not found:
                    new_lines.append(f"TIKTOK_SESSION_ID={sessionid}\n")
                    
                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                    
                print("✅ .env 파일에 TIKTOK_SESSION_ID를 완벽하게 저장했습니다!")
                time.sleep(2)
                break
                
            time.sleep(2)
            
        browser.close()

if __name__ == "__main__":
    extract_tiktok_session()
