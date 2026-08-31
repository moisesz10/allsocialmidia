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
            
    print("Post button visible:", page.locator("ytd-button-renderer#submit-button").first.is_visible())
    print("Schedule button visible:", page.locator("ytd-button-renderer#schedule-button").first.is_visible())
    print("Post button by role visible:", page.get_by_role("button", name="Post").is_visible() or page.get_by_role("button", name="Postar").is_visible())
    try:
        print("Schedule button by role visible:", page.get_by_role("button", name="Schedule").is_visible() or page.get_by_role("button", name="Programar").first.is_visible())
    except:
        pass
