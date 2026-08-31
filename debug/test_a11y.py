from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = context.pages[0]
    for p_ in context.pages:
        if 'youtube.com' in p_.url:
            page = p_
            break
    
    snapshot = page.accessibility.snapshot()
    with open("a11y.json", "w") as f:
        json.dump(snapshot, f, indent=2)
