import sys
import time
from playwright.sync_api import sync_playwright

def upload_images():
    print("Starting Playwright CDP connection...")
    with sync_playwright() as p:
        try:
            # Connect to existing browser
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("Connected to browser.")
            
            # Find the YouTube Studio Customization page
            context = browser.contexts[0]
            page = None
            for p in context.pages:
                if 'editing/profile' in p.url or 'studio.youtube.com/channel' in p.url:
                    page = p
                    break
            
            if not page:
                print("Could not find the YouTube Studio page.")
                return
            
            print(f"Found page: {page.url}")
            
            # Paths to the images we generated
            profile_pic_path = "/home/moises/.gemini/antigravity-ide/brain/28d3ea8c-3537-4413-b3ab-8d5df9b4b9d0/stoic_channel_logo_1787440554985.png"
            banner_pic_path = "/home/moises/.gemini/antigravity-ide/brain/28d3ea8c-3537-4413-b3ab-8d5df9b4b9d0/stoic_channel_banner_1787442553054.png"

            # 1. Upload Profile Picture
            print("Uploading Profile Picture...")
            with page.expect_file_chooser() as fc_info:
                # Click the Upload button in the Picture section
                page.locator("span:has-text('Foto')").locator("xpath=../..").locator("button:has-text('Enviar')").first.click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(profile_pic_path)
            time.sleep(1)
            
            # Click Done on the crop modal
            print("Confirming Profile Picture crop...")
            page.locator("button:has-text('Pronto')").first.click()
            time.sleep(2)
            
            # 2. Upload Banner Image
            print("Uploading Banner Image...")
            with page.expect_file_chooser() as fc_info:
                # Click the Upload button in the Banner image section
                page.locator("span:has-text('Imagem do banner')").locator("xpath=../..").locator("button:has-text('Enviar')").first.click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(banner_pic_path)
            time.sleep(1)
            
            # Click Done on the crop modal
            print("Confirming Banner crop...")
            page.locator("button:has-text('Pronto')").first.click()
            time.sleep(2)

            # 3. Publish changes
            print("Publishing changes...")
            page.locator("button:has-text('Publicar')").first.click()
            time.sleep(3)
            
            print("Upload completed successfully!")

        except Exception as e:
            print(f"Error during automation: {e}")

if __name__ == '__main__':
    upload_images()
