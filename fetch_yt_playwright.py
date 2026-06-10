from playwright.sync_api import sync_playwright

def get_yt_info(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        # Wait for the title and description to load
        page.wait_for_selector('h1.ytd-watch-metadata', timeout=10000)
        
        title = page.title()
        try:
            # Click the 'more' button in description to expand it if necessary
            page.locator('#expand').click(timeout=3000)
        except:
            pass
            
        description = page.locator('div#description-inline-expander').inner_text()
        
        print("TITLE:", title)
        print("DESCRIPTION:", description)
        browser.close()

if __name__ == "__main__":
    get_yt_info("https://www.youtube.com/watch?v=zvnbF9-Y_4w")
