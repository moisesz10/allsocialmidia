from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = context.pages[0]
    for p_ in context.pages:
        if 'youtube.com' in p_.url:
            page = p_
            break
            
    try:
        # Reload
        page.goto("https://www.youtube.com/@OEstoicoModerno/community")
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        page.screenshot(path="community_page.png")
        print("Screenshot saved.")
        
        # Look for the new post box
        locs = ["#commentbox-placeholder", "ytd-backstage-post-creation-renderer #placeholder", "#placeholder-area"]
        for loc in locs:
            print(f"{loc} visible:", page.locator(loc).first.is_visible())
    except Exception as e:
        print("Error:", e)
