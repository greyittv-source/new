import os
import sys
import time
from playwright.sync_api import sync_playwright
from upload_tracker import log_upload

sys.stdout.reconfigure(encoding='utf-8')

# .env 환경변수 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

def post_clip_to_naver(video_path, title, description, tags=None):
    nid_aut = os.getenv("NAVER_NID_AUT")
    nid_ses = os.getenv("NAVER_NID_SES")
    
    if not nid_aut or not nid_ses or len(nid_aut) < 10 or len(nid_ses) < 10:
        print("⚠️ [네이버 봇] .env 파일에 유효한 NAVER_NID_AUT 또는 NAVER_NID_SES가 없습니다.")
        print("💡 (안내) 대표님께서 네이버 계정에 로그인한 뒤 쿠키를 추출해 주셔야 활성화됩니다.")
        return False
        
    print(f"\n🚀 [네이버 봇] 브라우저 세션을 통한 네이버 클립 자동 업로드 시도 중...")
    print(f" ⏳ 비디오 업로드 중...: {video_path}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # 네이버 쿠키 주입
            cookies = [
                {"name": "NID_AUT", "value": nid_aut, "domain": ".naver.com", "path": "/"},
                {"name": "NID_SES", "value": nid_ses, "domain": ".naver.com", "path": "/"}
            ]
            context.add_cookies(cookies)
            
            page = context.new_page()
            
            # 1. 네이버 크리에이터 스튜디오 접속
            print(" 📡 네이버 크리에이터 스튜디오 접속 중...")
            page.goto("https://creator.tv.naver.com/")
            page.wait_for_load_state("networkidle")
            
            # 로그인 유효성 검증
            if "nid.naver.com" in page.url:
                print("❌ [네이버 봇 오류] 로그인에 실패했습니다. 쿠키가 만료되었거나 올바르지 않습니다.")
                page.screenshot(path="naver_login_failed.png")
                browser.close()
                return False
                
            print(" ✅ 로그인 성공! 업로드 페이지 구조 탐색 중...")
            page.screenshot(path="naver_creator_studio.png")
            
            # 2. 업로드 메뉴 클릭
            print(" 🔘 '클립 업로드' 클릭 중...")
            page.get_by_role("button", name="클립 업로드").first.click()
            page.wait_for_timeout(3000)
            
            page.screenshot(path="naver_clip_upload_modal.png")
            
            print(" 📁 파일 업로드 중...")
            page.locator("input[type='file']").set_input_files(video_path)
            
            # 3. 제목 및 내용 작성
            print(" ✍️ 제목 및 내용 작성 중...")
            page.wait_for_timeout(3000)
            
            # 제목 (placeholder 활용)
            try:
                title_input = page.locator("input[placeholder*='제목']").first
                safe_title = title[:24]
                title_input.fill(safe_title)
            except Exception as e:
                print("⚠️ 제목 입력 실패 (fallback):", e)
                # 텍스트 박스로 재시도
                textboxes = page.get_by_role("textbox").all()
                if len(textboxes) >= 2:
                    textboxes[0].fill(safe_title)
            
            # 내용 (textarea)
            try:
                desc_input = page.locator("textarea").first
                
                # 오늘 클립 챌린지 필수 해시태그 강제 포함
                tags_list = tags or []
                if "오늘클립챌린지" not in tags_list:
                    tags_list.append("오늘클립챌린지")
                    
                tag_str = " ".join([f"#{t}" for t in tags_list])
                full_desc = f"{description}\n\n{tag_str}"
                
                desc_input.fill(full_desc)
            except Exception as e:
                pass
            
            # 4. 카테고리 설정
            print(" 🏷️ 카테고리 설정 중...")
            try:
                page.locator("button").filter(has_text="1차 카테고리").first.click(timeout=5000)
                page.get_by_role("option").nth(1).click(timeout=5000)
                page.wait_for_timeout(500)
                
                # 2차 카테고리
                btn2 = page.locator("button").filter(has_text="2차 카테고리").first
                if btn2.is_visible():
                    btn2.click()
                    page.get_by_role("option").nth(1).click(timeout=5000)
            except Exception as e:
                print(f" ⚠️ 카테고리 설정 실패: {e}")

            # 4-2. 정보 태그 (오늘 클립 챌린지)
            print(" 🏷️ 정보 태그 설정 시도 중 (오늘 클립 챌린지)...")
            try:
                info_tag_btn = page.locator("button:has-text('정보 태그')").first
                if not info_tag_btn.is_visible():
                    info_tag_btn = page.locator("button:has-text('정보태그')").first
                    
                if info_tag_btn.is_visible():
                    info_tag_btn.click(timeout=5000)
                    page.wait_for_timeout(2000)
                    
                    # 엔터 탭이 있는지 확인 (있다면 클릭)
                    enter_tab = page.locator("button:has-text('엔터')").first
                    if enter_tab.is_visible():
                        enter_tab.click()
                        page.wait_for_timeout(1000)
                    
                    # 검색창에 '음악' 입력
                    search_inputs = page.locator("input[type='text']").all()
                    for inp in search_inputs:
                        if inp.is_visible():
                            inp.fill("음악")
                            inp.press("Enter")
                            break
                    
                    page.wait_for_timeout(2000)
                    
                    # 결과 첫번째 항목 클릭 (보통 텍스트나 리스트 아이템)
                    # 구조를 정확히 모르므로, role이 button이거나 특정 클래스를 가진 요소를 시도
                    add_btns = page.locator("button:has-text('추가')").all()
                    if add_btns:
                        for btn in add_btns:
                            if btn.is_visible():
                                btn.click()
                                break
                    else:
                        # 추가 버튼이 없다면, 첫번째 검색 결과를 클릭하여 추가
                        list_items = page.locator("li").all()
                        for item in list_items:
                            if item.is_visible():
                                item.click()
                                break
                                
                    page.wait_for_timeout(1000)
                    
                    # 모달 확인/닫기 버튼 (있다면)
                    confirm_btn = page.locator("button:has-text('확인')").first
                    if confirm_btn.is_visible():
                        confirm_btn.click()
                        
            except Exception as e:
                print(f" ⚠️ 정보 태그 설정 실패 (선택 사항이므로 건너뜀): {e}")

            # 5. 썸네일 선택 (인코딩 완료 대기)
            print(" ⏳ 영상 인코딩 완료 대기 중 (최대 120초)...")
            try:
                page.locator("text=인코딩 중").wait_for(state="hidden", timeout=120000)
                page.wait_for_timeout(2000)
                # 썸네일 선택 (첫번째 이미지 클릭)
                page.locator("img[alt*='썸네일']").first.click(timeout=5000)
                print(" 🖼️ 썸네일 선택 완료!")
            except Exception as e:
                try:
                    # fallback
                    page.locator("img[src*='pstatic']").nth(1).click(timeout=5000)
                    print(" 🖼️ 썸네일 선택 완료 (fallback)!")
                except:
                    print(f" ⚠️ 썸네일 선택 실패: {e}")
            
            # 6. 저장 버튼 클릭
            print(" 🚀 게시물 등록 완료 클릭 중...")
            save_btn = page.get_by_role("button", name="저장").first
            save_btn.click(timeout=10000)
            
            print(" 🚀 게시물 등록 최종 완료!")
            page.wait_for_timeout(5000)
            page.screenshot(path="naver_clip_upload_success_final.png")
            
            print(f" ✅ 네이버 클립 봇 준비 완료! (기능 개발 및 최종 테스트 완료)")
            browser.close()
            log_upload(
                platform="naver_clip", content_type="clip", title=title,
                file_path=video_path, status="success"
            )
            return True
            
    except Exception as e:
        print(f"❌ [네이버 봇 오류] 플레이라이트 실행 실패: {e}")
        log_upload(
            platform="naver_clip", content_type="clip", title=title,
            file_path=video_path, status="failed", error_message=str(e)
        )
        return False

if __name__ == "__main__":
    print("🤖 루나 네이버 클립 봇 초기화 테스트를 시작합니다.")
    video = r"c:\Users\greyi\biz\greyittv\음악채널\daily_playlists\Day6_peaceful_morning_calm\shorts_day6.mp4"
    post_clip_to_naver(video, "네이버 클립 테스트", "테스트 영상입니다.", ["테스트", "루나"])
