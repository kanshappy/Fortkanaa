import os
import requests
import tweepy

# 1. Credentials
consumer_key = os.environ["X_API_KEY"].strip()
consumer_secret = os.environ["X_API_SECRET"].strip()
access_token = os.environ["X_ACCESS_TOKEN"].strip()
access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"].strip()
fn_key = os.environ.get("FN_API_KEY", "").strip()

# 2. Fetch Shop Data & Find Valid Image
headers = {"Authorization": fn_key} if fn_key else {}
shop_res = requests.get("https://fortnite-api.com/v2/shop", headers=headers).json()

img_url = None

# Case 1: Direct composite
if "data" in shop_res:
    data = shop_res["data"]
    if isinstance(data, dict):
        img_url = data.get("composite")
        
        # Case 2: Featured first item display asset / newDisplayAsset
        if not img_url:
            for section in ["featured", "daily"]:
                entries = data.get(section, {}).get("entries", []) if isinstance(data.get(section), dict) else []
                if entries:
                    for entry in entries:
                        new_asset = entry.get("newDisplayAsset", {})
                        if new_asset and new_asset.get("materialInstances"):
                            for inst in new_asset["materialInstances"]:
                                images = inst.get("images", {})
                                if images.get("Background"):
                                    img_url = images["Background"]
                                    break
                        if not img_url and entry.get("items"):
                            for itm in entry["items"]:
                                img_url = itm.get("images", {}).get("featured") or itm.get("images", {}).get("icon")
                                if img_url:
                                    break
                        if img_url:
                            break
                if img_url:
                    break

# Fallback clean direct high-res store render
if not img_url:
    img_url = "https://bot.fnbr.co/shop.png"

print(f"Downloading image from: {img_url}")

# Download binary image
headers_img = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(img_url, headers=headers_img, stream=True)

with open("shop.png", "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

# 3. Twitter Auth (OAuth 1.0a for Media Upload)
auth = tweepy.OAuth1UserHandler(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
api = tweepy.API(auth)

# Upload media
media = api.media_upload(filename="shop.png")

# 4. Tweet Post via Twitter API v2
client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

caption = """Fortnite Item Shop Update! 🛒🔥

#Fortnite #ItemShop #FortniteItemShop"""

client.create_tweet(text=caption, media_ids=[media.media_id])
print("Successfully posted to X!")
