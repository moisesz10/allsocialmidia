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
        print("Clicking Schedule post...")
        # Make sure the menu is open first, if it closed
        if not page.get_by_text("Schedule post").is_visible():
            page.locator("#option-menu button").last.click(force=True)
            time.sleep(1)
            
        page.get_by_text("Schedule post").click(force=True)
        time.sleep(3)
        page.screenshot(path="after_schedule_click.png")
        print("Screenshot saved.")
    except Exception as e:
        print("Error:", e)
