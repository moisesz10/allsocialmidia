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
        # Assuming we are on the post creation dialog
        # 1. Type text to enable buttons
        print("Typing text...")
        page.locator("#contenteditable-root").first.fill("Test post for schedule dialog")
        time.sleep(2)
        
        # 2. Open schedule menu
        print("Clicking action menu...")
        page.locator("#option-menu button").last.click(force=True)
        time.sleep(2)
        
        # 3. Click last paper item (Schedule post)
        print("Clicking Schedule post...")
        page.locator("tp-yt-paper-item").last.click(force=True)
        time.sleep(3)
        
        page.screenshot(path="after_schedule_click.png")
        print("Screenshot saved.")
        
        # Output the new dialog HTML
        el_html = page.evaluate("""() => {
            const dialog = document.querySelector('tp-yt-paper-dialog[aria-hidden="false"]') || document.querySelector('ytd-metadata-update-dialog-renderer') || document.body;
            return dialog.innerHTML;
        }""")
        with open("schedule_dialog_html.html", "w", encoding='utf-8') as f:
            f.write(el_html)
    except Exception as e:
        print("Error:", e)
