from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = context.pages[0]
    for p_ in context.pages:
        if 'youtube.com' in p_.url:
            page = p_
            break
    
    print("Trying textbox role...")
    tb = page.get_by_role("textbox").all()
    for i, t in enumerate(tb):
        print(f"Textbox {i} visible: {t.is_visible()}")
        
    print("Trying to click textbox...")
    try:
        page.get_by_role("textbox").last.click(force=True, timeout=2000)
        print("Clicked last textbox")
    except Exception as e:
        print("Could not click", e)
        
    page.screenshot(path="after_click_role.png")
