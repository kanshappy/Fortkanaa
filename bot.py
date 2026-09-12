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

# Try composite
if isinstance(data, dict):
    img_url = data.get("composite")

# Extract image from active entries if composite is not present
if not img_url and isinstance(data, dict):
    entries = data.get("entries", [])
    for entry in entries:
        # Check bundle preview
        if entry.get("bundle") and entry["bundle"].get("image"):
            img_url = entry["bundle"]["image"]
            break
        # Check display assets
        render = entry.get("newDisplayAsset", {}).get("materialInstances", [{}])[0].get("images", {}).get("Background")
        if render:
            img_url = render
            break
        # Check cosmetic item icons
        items = entry.get("items", [])
        if items:
            img_url = items[0].get("images", {}).get("featured") or items[0].get("images", {}).get("icon")
            if img_url:
                break

# Guaranteed live Fortnite cosmetic fallback image
if not img_url:
    img_url = "https://fortnite-api.com/images/cosmetics/br/cid_028_athena_commando_f/icon.png"

print(f"Downloading from: {img_url}")

# Download full image
img_resp = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)

with open("shop.png", "wb") as f:
    f.write(img_resp.content)

file_size = os.path.getsize("shop.png")
print(f"Downloaded file size: {file_size} bytes")

# Ensure image is valid (not 63 bytes error response)
if file_size < 5000:
    raise ValueError(f"Downloaded file is too small ({file_size} bytes). Invalid image source.")

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

# 4. Tweet using v2 Client
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
