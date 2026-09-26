import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    video_dir = "/config/Desktop/BuildWithGemini/wardrobe-stylist/demo/recordings"
    os.makedirs(video_dir, exist_ok=True)
    # Clear old webm files
    for f in os.listdir(video_dir):
        if f.endswith(".webm"):
            os.remove(os.path.join(video_dir, f))
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 950},
            record_video_dir=video_dir,
            record_video_size={"width": 1440, "height": 950}
        )
        page = await context.new_page()
        
        print("Navigating to WardrobeAI frontend...")
        await page.goto("http://localhost:8080", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Action 1: What our app does best — outfit curation tailored to wardrobe
        print("Action 1: Clicking example prompt pill...")
        pill = page.locator("button.prompt-btn:has-text('Curate a casual outfit')")
        await pill.click()
        
        # Wait for agent response
        print("Waiting for outfit curation response...")
        await page.wait_for_selector(".msg-wrapper.agent .bubble:not(:text('…'))", timeout=60000)
        await asyncio.sleep(3)
        
        # Smooth scroll through results
        await page.evaluate("() => { document.getElementById('log').scrollTo({top: document.getElementById('log').scrollHeight, behavior: 'smooth'}); }")
        await asyncio.sleep(2)
        
        # Action 2: Requested prompt: casual wear for a summer day with flowers on them
        print("Action 2: Typing summer floral casual wear prompt...")
        input_elem = page.locator("#input")
        prompt_text = "Generate a casual wear outfit for a sunny summer day with vibrant floral patterns on it."
        await input_elem.click()
        for char in prompt_text:
            await input_elem.type(char, delay=28)
        await asyncio.sleep(1)
        
        print("Submitting summer floral prompt...")
        await page.locator("form button").click()
        
        # Wait for the second agent reply
        print("Waiting for second agent response...")
        await page.wait_for_function(
            "() => document.querySelectorAll('.msg-wrapper.agent').length >= 2 && !document.querySelectorAll('.msg-wrapper.agent')[1].querySelector('.bubble').textContent.includes('…')",
            timeout=90000
        )
        
        # Wait for any <img> inside .a2card to finish loading
        print("Waiting for floral outfit image to load completely...")
        try:
            await page.wait_for_selector(".a2card img", state="visible", timeout=20000)
            await page.wait_for_function(
                "() => { const img = document.querySelector('.a2card img'); return img && img.complete && img.naturalHeight !== 0; }",
                timeout=20000
            )
        except Exception as e:
            print("Note on image waiting:", e)
            
        await asyncio.sleep(2)
        
        # Center and smoothly scroll directly to the generated card / image so the full image and card are in prime focus
        print("Scrolling into full view of the floral summer image card...")
        await page.evaluate("""() => {
            const img = document.querySelector('.a2card img');
            if (img) {
                img.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                const log = document.getElementById('log');
                log.scrollTo({ top: log.scrollHeight, behavior: 'smooth' });
            }
        }""")
        
        # Hold steady on the full summer floral image showcase so viewers can appreciate the full design
        await asyncio.sleep(6)
        
        # Smoothly scroll up slightly to show complete dialogue context
        await page.evaluate("""() => {
            const card = document.querySelector('.msg-wrapper:last-child .a2card') || document.querySelector('.a2card img');
            if (card) {
                card.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }""")
        await asyncio.sleep(4)
        
        await page.close()
        await context.close()
        await browser.close()
        print("Browser recording complete!")

if __name__ == "__main__":
    asyncio.run(run())
