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
            
    el_html = page.evaluate("""() => {
        // Find the button that contains "Post" text, and then find the dropdown arrow
        const postBtn = document.querySelector('#submit-button');
        if (postBtn) {
            let parent = postBtn.parentElement;
            return parent.outerHTML;
        }
        return "Not found";
    }""")
    with open("dropdown_html.html", "w") as f:
        f.write(el_html)
