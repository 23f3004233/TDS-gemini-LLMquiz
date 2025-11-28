"""
Web scraper tool using Playwright for JavaScript-rendered pages
"""
from langchain_core.tools import tool
from playwright.async_api import async_playwright
import asyncio

@tool
async def get_rendered_html(url: str) -> str:
    """
    Fetch and render a JavaScript-heavy webpage using Playwright.
    Returns the fully rendered HTML content after JavaScript execution.
    
    Args:
        url: The URL to fetch and render
    
    Returns:
        Fully rendered HTML content as string
    
    Example:
        html = await get_rendered_html("https://example.com/quiz-123")
    """
    print(f"🌐 Scraping URL: {url}")
    
    try:
        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            
            # Create new page
            page = await browser.new_page()
            
            # Set a reasonable timeout
            page.set_default_timeout(30000)  # 30 seconds
            
            try:
                # Navigate to URL and wait for network to be idle
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Additional wait for dynamic content
                await asyncio.sleep(2)
                
                # Get the fully rendered HTML
                html_content = await page.content()
                
                print(f"✅ Successfully scraped {len(html_content)} characters")
                
                return html_content
            
            finally:
                await browser.close()
    
    except Exception as e:
        error_msg = f"❌ Error scraping {url}: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}"