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
        time.sleep(3)
        
        # Click placeholder
        page.locator("#commentbox-placeholder").click(force=True)
        time.sleep(2)
        
        # Click and type text
        input_box = page.locator("div#contenteditable-root").first
        input_box.click(force=True)
        time.sleep(1)
        page.keyboard.type("Automated test")
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # Dispatch input event
        page.evaluate("""() => {
            const b = document.querySelectorAll('div#contenteditable-root')[0];
            if (b) b.dispatchEvent(new InputEvent('input', {bubbles:true}));
        }""")
        time.sleep(2)
        
        # Click action menu
        action_menu = page.locator("#option-menu button").last
        action_menu.click(force=True)
        time.sleep(2)
        
        # Click Schedule post
        page.locator("tp-yt-paper-item").last.click(force=True)
        time.sleep(3)
        
        # Dump the dialog HTML
        el_html = page.evaluate("""() => {
            const dialog = document.querySelector('tp-yt-paper-dialog[aria-hidden="false"]') || document.querySelector('ytd-metadata-update-dialog-renderer') || document.body;
            return dialog.innerHTML;
        }""")
        with open("schedule_dialog_html.html", "w", encoding='utf-8') as f:
            f.write(el_html)
            
        page.screenshot(path="after_schedule_click.png")
        print("Done.")
    except Exception as e:
        print("Error:", e)
