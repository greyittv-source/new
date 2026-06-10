import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def extract_instagram_session():
    print("\n🌐 [인스타 세션 추출기] 브라우저를 엽니다. 창이 뜨면 직접 인스타그램에 '로그인'해 주세요!")
    print(" (로그인만 완료하시면 제가 쿠키를 훔쳐서 자동으로 .env에 저장하고 닫겠습니다 😎)\n")
    
    with sync_playwright() as p:
        # headless=False로 설정하여 사용자에게 브라우저 화면이 보이게 함
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.instagram.com/")
        
        print("⏳ 로그인이 완료될 때까지 감시 중입니다...")
        
        while True:
            # 브라우저 쿠키 목록 가져오기
            cookies = context.cookies()
            
            # 'sessionid'라는 이름의 쿠키 찾기
            sessionid = next((c['value'] for c in cookies if c['name'] == 'sessionid'), None)
            
            if sessionid:
                print(f"\n🎉 빙고! sessionid 쿠키를 획득했습니다: {sessionid[:10]}... (보안상 앞부분만 출력)")
                
                # .env 파일에 추가
                with open(".env", "a", encoding="utf-8") as f:
                    f.write(f"\nIG_SESSIONID={sessionid}\n")
                    
                print("✅ .env 파일에 IG_SESSIONID를 완벽하게 저장했습니다!")
                time.sleep(2) # 성공 메시지 볼 시간 2초 부여
                break
                
            time.sleep(2) # 2초마다 쿠키 감시
            
        browser.close()

if __name__ == "__main__":
    extract_instagram_session()
