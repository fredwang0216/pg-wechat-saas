import requests
import base64

# Create a large base64 string (approx 3MB)
large_data = "A" * (3 * 1024 * 1024)
pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKwMTQAAAABJRU5ErkJggg=="

html = f"""
<h1>Test Poster</h1>
<p>This is a test of the poster generation system with LARGE data.</p>
<img src="data:image/png;base64,{pixel}" width="100" height="100" />
<!-- Hidden large data to simulate payload size -->
<div style="display:none">{large_data}</div>
"""

url = "http://localhost:8001/api/generate-poster"
payload = {
    "html": html,
    "title": "Debug Poster Large Payload"
}

print(f"Sending request to {url}...")
try:
    resp = requests.post(url, json=payload, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        with open("backend/test_poster.png", "wb") as f:
            f.write(resp.content)
        print("Success! Saved to backend/test_poster.png")
    else:
        print(f"Failed: {resp.text}")
except Exception as e:
    print(f"Request failed: {e}")
