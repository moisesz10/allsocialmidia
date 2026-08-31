from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = context.pages[0]
    for p_ in context.pages:
        if 'youtube.com' in p_.url:
            page = p_
            break
    # We use a javascript evaluator to find the element containing the placeholder
    el_html = page.evaluate("""() => {
        // find the leaf element with the text
        const iterator = document.createNodeIterator(document.body, NodeFilter.SHOW_TEXT);
        let node;
        while (node = iterator.nextNode()) {
            if (node.textContent.includes("Share an image") || node.textContent.includes("What's on your mind")) {
                let parent = node.parentElement;
                while (parent && parent.tagName !== 'BODY') {
                    if (parent.id || parent.className) {
                        return '<' + parent.tagName.toLowerCase() + ' id="' + parent.id + '" class="' + parent.className + '">';
                    }
                    parent = parent.parentElement;
                }
            }
        }
        return "Not found";
    }""")
    with open("el_html.html", "w") as f:
        f.write(el_html)
