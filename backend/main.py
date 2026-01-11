from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import PropertyGuruScraper
from ai_service import AIService
import uvicorn
import os

app = FastAPI(title="PropertyGuru to WeChat API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import Response
import requests
import cloudscraper

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
scraper = PropertyGuruScraper()
ai_service = AIService(api_key=GEMINI_API_KEY)
img_fetcher = cloudscraper.create_scraper()

@app.get("/api/proxy-image")
async def proxy_image(url: str):
    """Proxy image to bypass hotlinking protection and ensure WeChat can load it."""
    try:
        from curl_cffi import requests as cffi_requests
        
        # Use curl_cffi to mimic a browser, avoiding CDN blocks on Railway/bot IPs
        response = cffi_requests.get(
            url, 
            impersonate="chrome120", 
            timeout=15
        )
        
        if response.status_code == 200:
            return Response(
                content=response.content,
                media_type=response.headers.get('Content-Type', 'image/jpeg'),
                headers={"Cache-Control": "max-age=31536000"}
            )
    except Exception as e:
        print(f"Proxy error for {url}: {e}")
    raise HTTPException(status_code=500, detail="Could not proxy image")

class GenerateRequest(BaseModel):
    url: str
    mode: str = "note"

@app.post("/api/generate")
async def generate_article(request: GenerateRequest, req: Request):
    if not request.url or "propertyguru.com.sg" not in request.url:
        raise HTTPException(status_code=400, detail="Invalid PropertyGuru URL")
    
    try:
        # Get base URL for proxy links
        base_url = str(req.base_url).rstrip('/')
        
        # 1. Scrape listing
        listing_data = await scraper.scrape(request.url)
        
        # 2. Generate content using AI
        article = await ai_service.generate_wechat_article(listing_data, mode=request.mode)
        
        # 3. Add images to content_html for the editor (Nuclear Option: Base64 Embedding)
        image_html = '<div class="gallery" style="margin-top: 20px;">'
        # Limit to 5 images to prevent payload too large errors
        images_to_process = listing_data.get('images', [])[:5] 
        
        from curl_cffi import requests as cffi_requests
        import base64

        print(f"Processing {len(images_to_process)} images with Base64 embedding...")

        for img_url in images_to_process:
            try:
                # Download image on backend using the passed stealth credentials
                # Impersonate Chrome 120 so PropertyGuru lets us download
                img_resp = cffi_requests.get(img_url, impersonate="chrome120", timeout=10)
                if img_resp.status_code == 200:
                    b64_data = base64.b64encode(img_resp.content).decode('utf-8')
                    mime_type = img_resp.headers.get('Content-Type', 'image/jpeg')
                    src = f"data:{mime_type};base64,{b64_data}"
                    
                    image_html += f'<p style="text-align: center; margin-bottom: 20px;"><img src="{src}" alt="Property Image" style="max-width: 100%; border-radius: 8px; display: block; margin: 0 auto;" width="600" /></p>'
                else:
                    print(f"Failed to download image {img_url}: {img_resp.status_code}")
            except Exception as e:
                print(f"Base64 processing error for {img_url}: {e}")
        
        image_html += '</div>'
        
        article['content_html'] = f"{article.get('content_html', '')}{image_html}"
        
        return article
    except Exception as e:
        print(f"Error generating article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class PosterRequest(BaseModel):
    html: str
    title: str

@app.post("/api/generate-poster")
async def generate_poster(request: PosterRequest):
    """Render the provided HTML into a long poster image using Playwright."""
    from playwright.async_api import async_playwright
    
    # Wrap HTML in a mobile-optimized poster template
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
            body {{
                margin: 0;
                padding: 0;
                background-color: #f8fafc;
                font-family: 'Noto Sans SC', sans-serif;
                color: #1e293b;
            }}
            .poster {{
                width: 375px; /* Standard mobile width */
                background-color: white;
                margin: 0 auto;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                padding: 40px 24px;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 700;
                line-height: 1.3;
            }}
            .content {{
                padding: 24px;
                line-height: 1.6;
                font-size: 15px;
            }}
            .content h1, .content h2 {{
                color: #4f46e5;
                font-size: 20px;
                border-left: 4px solid #4f46e5;
                padding-left: 12px;
                margin-top: 24px;
            }}
            .content p {{
                margin-bottom: 16px;
                color: #475569;
            }}
            .content ul {{
                padding-left: 20px;
                color: #475569;
            }}
            .content li {{
                margin-bottom: 8px;
            }}
            .content img {{
                max-width: 100%;
                border-radius: 12px;
                margin-bottom: 16px;
                display: block;
            }}
            .footer {{
                padding: 30px 24px;
                background-color: #f1f5f9;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}
            .footer p {{
                margin: 0;
                font-size: 13px;
                color: #94a3b8;
            }}
            .footer-logo {{
                font-weight: 700;
                color: #4f46e5;
                font-size: 18px;
                margin-bottom: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="poster">
            <div class="header">
                <h1>{request.title}</h1>
            </div>
            <div class="content">
                {request.html}
            </div>
            <div class="footer">
                <div class="footer-logo">PropertyGuru to WeChat</div>
                <p>扫描或长按识别二维码关注更多优质房源</p>
                <!-- Space for QR code/Watermark -->
                <div style="width: 80px; height: 80px; background: #ddd; margin: 20px auto 0; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #666;">QR CODE</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 375, "height": 800}) # Initial height, will grow
        await page.set_content(full_html)
        
        # Wait for images to load if any
        await page.wait_for_timeout(2000)
        
        # Capture the full page height
        element = await page.query_selector('.poster')
        if not element:
            raise HTTPException(status_code=500, detail="Poster element not found")
            
        bounding_box = await element.bounding_box()
        if not bounding_box:
             raise HTTPException(status_code=500, detail="Poster element invisible")

        screenshot = await element.screenshot(type='png')
        await browser.close()
        
        return Response(content=screenshot, media_type="image/png")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
