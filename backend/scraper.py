import cloudscraper
import requests
from bs4 import BeautifulSoup
import re
import json
import asyncio
import os

class PropertyGuruScraper:
    def __init__(self):
        self.cloud_scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True
            },
            delay=2
        )
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }

    async def scrape(self, url: str):
        # Strategy 0: Curl CFFI with Rotation (Mobile First)
        # Mobile UAs often get lighter challenges
        impersonations = [
            "safari_ios_16_5",  # iPhone - Prioritize Mobile
            "chrome120",        # Desktop newest
            "safari15_5",       # Mac
            "chrome110",        # Desktop older
        ]
        
        from curl_cffi import requests as cffi_requests
        
        for imp in impersonations:
            print(f"Attempting to scrape with Curl Impersonate: {imp} on {url}")
            try:
                # Add random sleep to prevent burst detection
                await asyncio.sleep(1)
                
                response = cffi_requests.get(
                    url, 
                    impersonate=imp, 
                    headers=self.headers, 
                    timeout=20
                )
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    data = self._parse_soup(soup)
                    if data["title"] != "No Title" and not data["title"].startswith("[BLOCKED]"):
                        print(f"Curl CFFI success with {imp}!")
                        return data
                    else:
                        print(f"Curl CFFI {imp} was blocked.")
                else:
                    print(f"Curl CFFI {imp} failed status {response.status_code}")
                
                # Small delay before retry
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Curl CFFI error with {imp}: {e}")

        # Strategy 1: Cloudscraper (Legacy fast)
        print(f"Attempting to scrape with Cloudscraper: {url}")
        try:
            # cloudscraper is synchronous, but we can run it in a thread or just call it if we don't mind blocking briefly
            # Since this is a small FastAPI app, we'll use loop.run_in_executor for better performance if needed, 
            # but for now, simple call.
            response = self.cloud_scraper.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                data = self._parse_soup(soup)
                if data["title"] != "No Title" and not data["title"].startswith("[BLOCKED]"):
                    print("Cloudscraper success!")
                    return data
            print(f"Cloudscraper failed (Status {response.status_code}).")
        except Exception as e:
            print(f"Cloudscraper error: {e}")

        # Strategy 2: Playwright (Headed + Stealth fallback)
        print("Falling back to Playwright...")
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth
        
        async with async_playwright() as p:
            import tempfile
            user_data_dir = os.path.join(tempfile.gettempdir(), "pg_scraper_user_data_v2")
            
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=True, # Try headless first with stealth
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            )
            
            page = await context.new_page()
            await Stealth().apply_stealth_async(page)
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Wait for the challenge to pass (look for the title element)
                # Cloudflare challenge usually takes 5-10s
                try:
                    await page.wait_for_selector('h1', timeout=30000)
                except:
                    print("Timeout waiting for h1, might still be challenged.")

                # Scroll to trigger lazy loading
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(2)
                
                # Explicit wait for images (Reference Agent Logic)
                try:
                    await page.wait_for_selector('img', timeout=10000)
                except:
                    print("Timeout waiting for images")
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                data = self._parse_soup(soup)
                return data
            except Exception as e:
                print(f"Playwright fallback error: {e}")
                return {"title": "Error: Scraper blocked", "price": "", "address": "", "description": "", "images": []}
            finally:
                await context.close()

    def _parse_soup(self, soup):
        data = {
            "title": "No Title",
            "price": "Price on ask",
            "address": "",
            "description": "",
            "images": []
        }

        # Check for block (Strict)
        page_text = soup.get_text()
        block_keywords = [
            "Just a moment", 
            "Access Denied", 
            "Bot Protection Detected",
            "Checking your browser",
            "Attention Required",
            "Cloudflare"
        ]
        
        # Check title first
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text()
            if any(k.lower() in title_text.lower() for k in block_keywords):
                 data["title"] = "[BLOCKED] Bot Protection Detected"
                 return data

        # Check strict keywords in body only if title is missing or suspicious
        if any(k in page_text for k in block_keywords) and len(page_text) < 2000:
             # Assume it's a block page if it's short and contains keywords
             data["title"] = "[BLOCKED] Bot Protection Detected"
             return data

        # 1. Try JSON-LD or NEXT_DATA first (Internal Logic)
        # (Keeping the robust logic from previous step)
        ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in ld_scripts:
            try:
                ld_data = json.loads(script.string)
                items = ld_data if isinstance(ld_data, list) else [ld_data]
                for item in items:
                    if item.get("@type") in ["RealEstateListing", "Product", "Accommodation"]:
                        data["title"] = item.get("name") or data["title"]
                        data["description"] = item.get("description") or data["description"]
                        if "offers" in item and isinstance(item["offers"], dict):
                            data["price"] = f"{item['offers'].get('priceCurrency', 'SGD')} {item['offers'].get('price', '')}"
                        if "spatialCoverage" in item and isinstance(item["spatialCoverage"], dict):
                            data["address"] = item["spatialCoverage"].get("address", {}).get("streetAddress", data["address"])
                        
                        # Extract images from JSON-LD
                        if "image" in item:
                            imgs = item["image"]
                            if isinstance(imgs, str):
                                data["images"].append(imgs)
                            elif isinstance(imgs, list):
                                data["images"].extend(imgs)
            except: continue

        # 2. Fallback to CSS Selectors (Refined with reference agent logic)
        if data["title"] == "No Title":
            title_tag = soup.select_one('h1[da-id="property-title"], h1.title, h1')
            if title_tag: data["title"] = title_tag.get_text(strip=True)
            
        if data["price"] == "Price on ask":
            # Reference agent used data-automation-id='overview-price-txt' or class 'amount'
            price_tag = soup.select_one('[data-automation-id="overview-price-txt"], .amount, h2[da-id="price-amount"]')
            if price_tag: data["price"] = price_tag.get_text(strip=True)
            
        if not data["address"]:
            # Reference agent used class 'full-address__address'
            addr_tag = soup.select_one('.full-address__address, p[da-id="property-address"], .address')
            if addr_tag: data["address"] = addr_tag.get_text(strip=True)
            
        if not data["description"]:
            desc_tag = soup.select_one('.listing-description, .description, [da-id="description-widget"]')
            if desc_tag: data["description"] = desc_tag.get_text(separator="\n", strip=True)

        # 3. Image Extraction with V800 Transformation
        # Reference agent suggested V800 suffix for high res
        gallery_imgs = soup.select('img')
        for img in gallery_imgs:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy')
            if src and "pgimgs.com" in src:
                # Exclude icons/avatars/UI elements
                exclude_patterns = [
                    'APHO', 'hui-svgicon', 'logo', 'avatar', 'icon', 
                    'navbar-', 'map-shortcut', 'flags', 'static'
                ]
                if any(x in src.lower() for x in exclude_patterns):
                    continue
                
                # Transform to high res if possible (V800)
                # Matches patterns like .V550, .R550X550 etc.
                high_res_src = re.sub(r'\.(V\d+|R\d+X\d+)(\.jpg|\.png)', r'.V800\2', src)
                if high_res_src not in data["images"]:
                    data["images"].append(high_res_src)
        
        data["images"] = list(dict.fromkeys(data["images"]))[:20]
        return data

if __name__ == "__main__":
    # Quick test
    import json
    async def test():
        scraper = PropertyGuruScraper()
        test_url = "https://www.propertyguru.com.sg/listing/for-sale-viva-vista-500010094" 
        print(f"Testing scraper with URL: {test_url}")
        data = await scraper.scrape(test_url)
        print("\nFinal Result:")
        print(json.dumps(data, indent=2))
    
    asyncio.run(test())
