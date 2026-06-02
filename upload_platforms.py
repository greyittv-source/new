import os
import asyncio
from playwright.async_api import async_playwright

USER_DATA_DIR = os.path.join(os.getcwd(), "browser_data")

async def setup_logins():
    """최초 1회 실행하여 틱톡, 네이버에 직접 로그인하고 세션(쿠키)을 저장합니다."""
    print("\n[셋업 모드] 브라우저를 엽니다. 각 사이트에 로그인해 주세요.")
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, # 화면을 띄워서 사용자가 직접 로그인하게 함
            channel="chrome" # 설치된 크롬 사용
        )
        page = await browser.new_page()
        
        # 각 플랫폼 로그인 페이지 안내
        platforms = {
            "네이버": "https://nid.naver.com/nidlogin.login",
            "틱톡": "https://www.tiktok.com/login"
        }
        
        for name, url in platforms.items():
            print(f"\n[{name}] 로그인 페이지로 이동합니다...")
            await page.goto(url)
            print(f"👉 {name} 로그인이 완료되면 터미널에서 엔터를 눌러주세요!")
            await asyncio.to_thread(input, "로그인 완료 후 엔터를 누르세요: ")
            
        await browser.close()
        print("\n✅ 모든 로그인 정보(쿠키)가 성공적으로 저장되었습니다!")
        print("이제 파이프라인에서 자동으로 영상을 업로드할 수 있습니다.")

async def upload_video(platform, video_path, title, tags):
    """지정된 플랫폼에 영상을 업로드합니다."""
    print(f"\n[{platform}] 업로드 자동화를 시작합니다: {title}")
    async with async_playwright() as p:
        # headless=True로 띄우면 백그라운드에서 동작 (사용자 방해 안함)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=True,
            channel="chrome"
        )
        page = await browser.new_page()
        
        try:
            if platform == "네이버클립":
                print("네이버 블로그/클립 업로드 페이지로 이동...")
                await page.goto("https://blog.naver.com/")
                # TODO: 실제 네이버 클립 업로드 HTML DOM Selector 클릭 자동화
                
            elif platform == "틱톡":
                print("틱톡 업로드 센터로 이동...")
                await page.goto("https://www.tiktok.com/creator-center/upload")
                # TODO: 틱톡 업로드 HTML DOM Selector 클릭 자동화
                
            await asyncio.sleep(3) # 실제 업로드 대기 시간 시뮬레이션
            print(f"✅ {platform} 업로드 시뮬레이션 완료!")
        except Exception as e:
            print(f"❌ {platform} 업로드 실패: {e}")
        finally:
            await browser.close()

def run_upload(platform, video_path, title, tags):
    """일반 동기식 파이프라인(main.py)에서 호출할 수 있는 래퍼 함수"""
    asyncio.run(upload_video(platform, video_path, title, tags))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        asyncio.run(setup_logins())
    else:
        print("업로드 테스트 모드: python upload_platforms.py setup 을 실행하여 로그인을 세팅하세요.")
