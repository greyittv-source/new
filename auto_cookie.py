import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    import browser_cookie3
except ImportError:
    print("모듈이 아직 설치 중입니다. 잠시 후 다시 시도해주세요.")
    sys.exit(1)

def grab_tiktok_cookie():
    print("🕵️‍♂️ 크롬/엣지 브라우저에서 틱톡 쿠키를 몰래 훔쳐오는 중...")
    try:
        # load() 함수는 시스템에 설치된 모든 브라우저(크롬, 엣지, 파이어폭스 등)를 스캔합니다.
        cj = browser_cookie3.load(domain_name='tiktok.com')
        sessionid = next((c.value for c in cj if c.name == 'sessionid'), None)
        
        if sessionid:
            print(f"🎉 성공적으로 틱톡 쿠키(sessionid)를 탈취했습니다: {sessionid[:10]}...")
            
            # .env에 저장
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
            
            print("✅ .env 파일에 완벽하게 꽂아 넣었습니다!")
        else:
            print("❌ 브라우저에 틱톡(tiktok.com) 로그인 정보가 없습니다.")
            print(" 크롬이나 엣지 브라우저를 열고 틱톡에 먼저 로그인해주세요!")
    except Exception as e:
        print(f"오류 발생: {e}")
        print("💡 팁: 열려있는 브라우저 창을 모두 끄고 다시 실행해 보세요!")

if __name__ == "__main__":
    grab_tiktok_cookie()
