from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = context.pages[0]
    for p_ in context.pages:
        if 'youtube.com' in p_.url:
            page = p_
            break
    page.bring_to_front()
    import time
    time.sleep(1)
    
    # Try different locators
    locators = [
        "ytd-backstage-post-creation-renderer #placeholder",
        "div#contenteditable-root",
        "ytd-backstage-post-creation-renderer",
        "ytd-creator-post-creation-renderer",
        "#placeholder",
        "ytd-backstage-post-creation-renderer div#contenteditable-root",
        "ytd-backstage-post-dialog-renderer #placeholder"
    ]
    for loc in locators:
        try:
            el = page.locator(loc).first
            print(f"Locator {loc} is_visible:", el.is_visible(timeout=1000))
        except Exception as e:
            print(f"Error {loc}: {e}")
            
    # Try text based
    try:
        el = page.get_by_text("What's on your mind?").first
        print(f"Text 'What's on your mind?' is_visible:", el.is_visible(timeout=1000))
        # click it
        el.click(force=True)
        print("Clicked on What's on your mind text!")
    except Exception as e:
        print(f"Error text: {e}")
        
    time.sleep(2)
    page.screenshot(path="after_click.png")
