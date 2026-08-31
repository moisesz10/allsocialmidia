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
        # Reload just to be safe
        page.goto("https://www.youtube.com/@OEstoicoModerno/community")
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # 1. Click placeholder
        print("Clicking placeholder...")
        page.locator("#commentbox-placeholder").click(force=True)
        time.sleep(2)
        
        # 2. Type text
        print("Typing text...")
        page.locator("#contenteditable-root").first.fill("Test post from automation tool")
        time.sleep(2)
        
        # 3. Open schedule menu
        print("Clicking action menu...")
        page.locator("#option-menu button").last.click(force=True)
        time.sleep(2)
        
        # 4. Click Schedule post
        print("Clicking Schedule post...")
        page.get_by_text("Schedule post").click(force=True)
        time.sleep(3)
        
        # 5. Take screenshot
        page.screenshot(path="after_schedule_click.png")
        print("Screenshot saved.")
        
        # 6. Output some HTML to see datepicker
        el_html = page.evaluate("""() => {
            return document.body.innerHTML;
        }""")
        with open("body_html.html", "w", encoding='utf-8') as f:
            f.write(el_html)
    except Exception as e:
        print("Error:", e)
