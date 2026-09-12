import os
import requests
import tweepy

# 1. Credentials
consumer_key = os.environ["X_API_KEY"].strip()
consumer_secret = os.environ["X_API_SECRET"].strip()
access_token = os.environ["X_ACCESS_TOKEN"].strip()
access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"].strip()
fn_key = os.environ.get("FN_API_KEY", "").strip()

# 2. Get Official Store Image from fortnite-api.com
headers = {"Authorization": fn_key} if fn_key else {}
api_res = requests.get("https://fortnite-api.com/v2/shop", headers=headers).json()

img_url = None
if "data" in api_res and isinstance(api_res["data"], dict):
    # Try composite first
    img_url = api_res["data"].get("composite")
    
    # Fallback to the latest featured item image
    if not img_url:
        for cat in ["featured", "daily"]:
            entries = api_res["data"].get(cat, {}).get("entries", [])
            for e in entries:
                items = e.get("items", [])
                for itm in items:
                    img_url = itm.get("images", {}).get("featured") or itm.get("images", {}).get("icon")
                    if img_url:
                        break
                if img_url:
                    break
            if img_url:
                break

if not img_url:
    # Direct reliable CDN fallback
    img_url = "https://media.fortniteapi.io/images/shop/en/full_shop.png"

print(f"Downloading image from: {img_url}")

img_req = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
with open("shop.png", "wb") as f:
    f.write(img_req.content)

print(f"File size downloaded: {os.path.getsize('shop.png')} bytes")

# Verify PNG/JPEG header to avoid HTML block pages
with open("shop.png", "rb") as f:
    header = f.read(4)
    if header.startswith(b"<html") or header.startswith(b"<!DO"):
        raise ValueError("Downloaded an HTML error page instead of an image.")

# 3. Twitter Auth (OAuth 1.0a User Context)
auth = tweepy.OAuth1UserHandler(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
api = tweepy.API(auth)

# Upload using chunked method for stability
media = api.media_upload(filename="shop.png", chunked=True)
print(f"Media uploaded successfully! Media ID: {media.media_id}")

# 4. Tweet Post via Twitter API v2
client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

caption = """Fortnite Item Shop Update! 🛒🔥

#Fortnite #ItemShop #FortniteItemShop"""

res = client.create_tweet(text=caption, media_ids=[media.media_id])
print("Successfully posted to X!")
