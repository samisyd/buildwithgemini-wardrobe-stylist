import asyncio
import os
import subprocess
from playwright.async_api import async_playwright

async def run():
    video_dir = "/config/Desktop/BuildWithGemini/wardrobe-stylist/demo/recordings"
    os.makedirs(video_dir, exist_ok=True)
    
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
            viewport={"width": 1280, "height": 800},
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 800}
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
        # Wait until agent bubble is no longer "…" and has actual rendered content
        await page.wait_for_selector(".msg-wrapper.agent .bubble:not(:text('…'))", timeout=60000)
        await asyncio.sleep(4)
        
        # Smooth scroll through results
        await page.evaluate("() => { document.getElementById('log').scrollTop = document.getElementById('log').scrollHeight; }")
        await asyncio.sleep(2)
        
        # Action 2: Richer prompt showing tool calls / database lookup & image generation
        print("Action 2: Typing richer prompt for database inspection & visual rendering...")
        input_elem = page.locator("#input")
        prompt_text = "Search my wardrobe catalog for jackets and generate a styled photo of a classic trench coat look."
        await input_elem.click()
        for char in prompt_text:
            await input_elem.type(char, delay=35)
        await asyncio.sleep(1)
        
        print("Submitting richer prompt...")
        await page.locator("form button").click()
        
        # Wait for the second agent reply
        print("Waiting for second agent response...")
        await page.wait_for_function(
            "() => document.querySelectorAll('.msg-wrapper.agent').length >= 2 && !document.querySelectorAll('.msg-wrapper.agent')[1].querySelector('.bubble').textContent.includes('…')",
            timeout=90000
        )
        await asyncio.sleep(6)
        
        # Scroll down smoothly to show the complete dialogue and visual card
        await page.evaluate("() => { document.getElementById('log').scrollTop = document.getElementById('log').scrollHeight; }")
        await asyncio.sleep(4)
        
        # Close page and context to finalize video recording
        await page.close()
        await context.close()
        await browser.close()
        print("Browser recording complete!")

if __name__ == "__main__":
    asyncio.run(run())
