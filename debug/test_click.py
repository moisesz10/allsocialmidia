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
        print("Clicking #commentbox-placeholder...")
        page.locator("#commentbox-placeholder").click(force=True, timeout=3000)
        time.sleep(2)
        print("Looking for #contenteditable-root...")
        if page.locator("#contenteditable-root").is_visible():
            print("#contenteditable-root is VISIBLE!")
            page.locator("#contenteditable-root").first.type("Testing post automation")
        else:
            print("#contenteditable-root is still hidden")
    except Exception as e:
        print("Error:", e)
        
    page.screenshot(path="after_test_click.png")
