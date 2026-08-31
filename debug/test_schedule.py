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
        print("Clicking action menu...")
        # Since it's yt-button-shape inside ytd-menu-renderer inside #option-menu
        page.locator("#option-menu button").last.click(force=True)
        time.sleep(2)
        page.screenshot(path="after_action_menu.png")
        print("Dropdown clicked.")
        
        # Now find the schedule option
        # It's likely a menu item
        print("Checking for paper-item texts...")
        items = page.locator("tp-yt-paper-item").all_inner_texts()
        print("Paper items:", items)
    except Exception as e:
        print("Error:", e)
