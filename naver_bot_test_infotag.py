import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
NAVER_COOKIE_NID_AUT = os.getenv("NAVER_COOKIE_NID_AUT", "")
NAVER_COOKIE_NID_SES = os.getenv("NAVER_COOKIE_NID_SES", "")

def test_infotag():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        context.add_cookies([
            {"name": "NID_AUT", "value": NAVER_COOKIE_NID_AUT, "domain": ".naver.com", "path": "/"},
            {"name": "NID_SES", "value": NAVER_COOKIE_NID_SES, "domain": ".naver.com", "path": "/"}
        ])
        
        page = context.new_page()
        page.goto("https://creator.tv.naver.com/")
        page.wait_for_timeout(3000)
        
        # 클립 업로드 클릭
        page.get_by_role("button", name="클립 업로드").first.click()
        page.wait_for_timeout(3000)
        
        # 정보 태그 버튼 클릭
        try:
            info_tag_btn = page.locator("button:has-text('정보 태그')").first
            if not info_tag_btn.is_visible():
                info_tag_btn = page.locator("button:has-text('정보태그')").first
            info_tag_btn.click()
            page.wait_for_timeout(2000)
            
            page.screenshot(path="naver_infotag_modal.png")
            html = page.content()
            with open("naver_infotag.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("✅ 정보 태그 모달 덤프 성공!")
        except Exception as e:
            print("⚠️ 정보 태그 버튼 클릭 실패:", e)
            
        browser.close()

if __name__ == "__main__":
    test_infotag()
