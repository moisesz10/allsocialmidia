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
        page.get_by_text("Schedule post").click(force=True)
        time.sleep(2)
        print("Date picker visible:", page.locator("ytcp-text-dropdown-trigger#datepicker-trigger").is_visible())
        print("Time picker visible:", page.locator("ytcp-text-dropdown-trigger#time-of-day-trigger").is_visible())
        
        # Dump the HTML of the dialog to find locators
        el_html = page.evaluate("""() => {
            const dialog = document.querySelector('ytd-backstage-post-dialog-renderer') || document.body;
            return dialog.innerHTML;
        }""")
        with open("dialog_html.html", "w", encoding='utf-8') as f:
            f.write(el_html)
    except Exception as e:
        print("Error:", e)
