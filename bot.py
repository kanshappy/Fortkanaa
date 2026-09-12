import os
import requests
import tweepy

# 1. Credentials
consumer_key = os.environ["X_API_KEY"].strip()
consumer_secret = os.environ["X_API_SECRET"].strip()
access_token = os.environ["X_ACCESS_TOKEN"].strip()
access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"].strip()
fn_key = os.environ.get("FN_API_KEY", "").strip()

# 2. Fetch Live Shop from Fortnite-API.com
headers = {"Authorization": fn_key} if fn_key else {}
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

api_url = "https://fortnite-api.com/v2/shop"
res = requests.get(api_url, headers=headers, timeout=20).json()

img_url = None
data = res.get("data", {})

if isinstance(data, dict):
    # Try composite first
    img_url = data.get("composite")

    # Safe extraction from shop entries
    if not img_url:
        entries = data.get("entries", [])
        for entry in entries:
            # 1. Bundle image
            bundle = entry.get("bundle") or {}
            if bundle.get("image"):
                img_url = bundle["image"]
                break

            # 2. Display asset background
            new_asset = entry.get("newDisplayAsset") or {}
            instances = new_asset.get("materialInstances") or []
            if instances and isinstance(instances, list) and len(instances) > 0:
                bg = (instances[0].get("images") or {}).get("Background")
                if bg:
                    img_url = bg
                    break

            # 3. Item icons
            items = entry.get("items") or []
            for item in items:
                images = item.get("images") or {}
                icon = images.get("featured") or images.get("icon")
                if icon:
                    img_url = icon
                    break
            if img_url:
                break

# Reliable direct fallback image
if not img_url:
    img_url = "https://fortnite-api.com/images/cosmetics/br/cid_028_athena_commando_f/icon.png"

print(f"Downloading from: {img_url}")

# Download binary image
img_resp = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
with open("shop.png", "wb") as f:
    f.write(img_resp.content)

file_size = os.path.getsize("shop.png")
print(f"Downloaded file size: {file_size} bytes")

if file_size < 1000:
    raise ValueError(f"Downloaded file is invalid: {file_size} bytes.")

# 3. Twitter API Auth & Media Upload
auth = tweepy.OAuth1UserHandler(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
api = tweepy.API(auth)
media = api.media_upload(filename="shop.png")
print(f"Uploaded successfully! Media ID: {media.media_id}")

# 4. Tweet via v2 Client
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
