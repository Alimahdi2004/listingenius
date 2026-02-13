"""
ListinGenius API - Vercel Serverless Function
Integrates Claude AI for descriptions and social posts
"""

import os
import json
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Try to import httpx for API calls
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

# API Keys from environment
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HF_API_KEY = os.environ.get("HF_API_KEY", "")
HF_API_SECRET = os.environ.get("HF_API_SECRET", "")


def generate_description(listing: dict) -> str:
    """Generate property description using Claude"""
    
    if not ANTHROPIC_API_KEY or not HTTPX_AVAILABLE:
        # Return demo description
        address = listing.get('address', '123 Main Street')
        return f"""Welcome to your dream home at {address}! This stunning property offers the perfect blend of comfort and elegance.

Step inside to discover an open-concept living space bathed in natural light, featuring gleaming hardwood floors and designer finishes throughout. The gourmet kitchen boasts premium appliances, quartz countertops, and a spacious island perfect for entertaining.

The primary suite is a true retreat with a spa-inspired ensuite and walk-in closet. Additional bedrooms offer flexibility for family, guests, or home office space.

Located in a sought-after neighborhood, this home won't last long. Schedule your private showing today!"""
    
    try:
        with httpx.Client(timeout=30.0) as client:
            prompt = f"""Write a compelling real estate listing description for:

Property Type: {listing.get('property_type', 'Single Family Home')}
Address: {listing.get('address', 'Beautiful Home')}
Price: ${listing.get('price', 500000):,.0f}
Bedrooms: {listing.get('bedrooms', 4)}
Bathrooms: {listing.get('bathrooms', 3)}
Square Feet: {listing.get('sqft', 'Not specified')}
Style: {listing.get('style', 'cinematic')}

Write 2-3 engaging paragraphs (150-200 words). No headers, just the description text."""

            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["content"][0]["text"]
    except Exception as e:
        print(f"Claude API error: {e}")
    
    # Fallback
    address = listing.get('address', '123 Main Street')
    return f"Welcome to {address}! This beautiful home awaits you. Contact us for a showing today!"


def generate_social_posts(listing: dict) -> dict:
    """Generate social media posts using Claude"""
    
    address = listing.get('address', '123 Main Street')
    price = listing.get('price', 500000)
    beds = listing.get('bedrooms', 4)
    baths = listing.get('bathrooms', 3)
    
    default_posts = {
        "instagram": f"JUST LISTED\n\n{address}\n${price:,.0f} | {beds} BD / {baths} BA\n\nDream home alert! Tap link in bio!\n\n#JustListed #RealEstate #DreamHome #HomeForSale",
        "facebook": f"NEW LISTING!\n\n{address}\n${price:,.0f}\n\n{beds} Bedrooms | {baths} Bathrooms\n\nContact me today for a private showing!",
        "tiktok": f"POV: You just found your dream home ${price:,.0f} | {beds}BD/{baths}BA #realestate #housetour #dreamhome #justlisted",
        "twitter": f"Just Listed: {address}\n${price:,.0f} | {beds}BD/{baths}BA\nDM for details! #RealEstate",
        "youtube": f"{address} | Home Tour | ${price:,.0f} | {beds} BD / {baths} BA\n\nTake a virtual tour of this incredible property..."
    }
    
    if not ANTHROPIC_API_KEY or not HTTPX_AVAILABLE:
        return default_posts
    
    try:
        with httpx.Client(timeout=30.0) as client:
            prompt = f"""Create social media posts for this real estate listing:

Address: {address}
Price: ${price:,.0f}
Specs: {beds} BD / {baths} BA
Type: {listing.get('property_type', 'Single Family Home')}

Return ONLY a JSON object with posts for: instagram, facebook, tiktok, twitter, youtube
No markdown, no explanation, just the JSON."""

            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data["content"][0]["text"]
                # Try to parse JSON from response
                import re
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    return json.loads(json_match.group())
    except Exception as e:
        print(f"Social posts error: {e}")
    
    return default_posts


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path == "/api" or path == "/api/":
            self.send_json({
                "service": "ListinGenius API",
                "status": "running",
                "version": "1.0.0",
                "ai_enabled": bool(ANTHROPIC_API_KEY)
            })
        elif path == "/api/health":
            self.send_json({
                "status": "healthy",
                "anthropic_configured": bool(ANTHROPIC_API_KEY),
                "higgsfield_configured": bool(HF_API_KEY)
            })
        else:
            self.send_error(404, "Not found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length else '{}'
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if path == "/api/generate/description":
            description = generate_description(data)
            self.send_json({"description": description})
            
        elif path == "/api/generate/social":
            posts = generate_social_posts(data)
            self.send_json({"social_posts": posts})
            
        elif path == "/api/demo/generate":
            description = generate_description(data)
            social_posts = generate_social_posts(data)
            self.send_json({
                "description": description,
                "social_posts": social_posts,
                "videos": {
                    "vertical": ["demo_vertical.mp4"],
                    "square": ["demo_square.mp4"],
                    "landscape": ["demo_landscape.mp4"]
                },
                "message": "Generation complete"
            })
        else:
            self.send_error(404, "Not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_cors_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_error(self, code, message):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
