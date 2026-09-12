import os
import requests
import tweepy

# 1. Credentials
consumer_key = os.environ["X_API_KEY"].strip()
consumer_secret = os.environ["X_API_SECRET"].strip()
access_token = os.environ["X_ACCESS_TOKEN"].strip()
access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"].strip()
fn_key = os.environ.get("FN_API_KEY", "").strip()

# 2. Get Real Image URL from Fortnite-API.com
headers = {"Authorization": fn_key} if fn_key else {}

# Priority 1: Check BR Combined endpoint
img_url = None
try:
    r = requests.get("https://fortnite-api.com/v2/shop/br/combined", headers=headers, timeout=15)
    data = r.json().get("data", {})
    img_url = data.get("composite") or (data.get("featured", {}).get("entries", [{}])[0].get("newDisplayAsset", {}).get("materialInstances", [{}])[0].get("images", {}).get("Background"))
except Exception:
    pass

# Priority 2: Standard shop endpoint fallback
if not img_url:
    try:
        r = requests.get("https://fortnite-api.com/v2/shop", headers=headers, timeout=15)
        data = r.json().get("data", {})
        img_url = data.get("composite")
    except Exception:
        pass

# Priority 3: Direct verified high-res shop render CDN
if not img_url:
    img_url = "https://media.fortniteapi.com/shop.png"

print(f"Downloading image from: {img_url}")

# Download binary with browser user-agent
download_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
response = requests.get(img_url, headers=download_headers, timeout=30)

if response.status_code != 200 or len(response.content) < 5000:
    # If combined fails, fetch Fortnite's primary daily featured icon as reliable backup
    print("Fallback to direct featured asset...")
    backup_url = "https://fortnite-api.com/images/cosmetics/br/cid_515_athena_commando_m_barbecue/icon.png"
    response = requests.get(backup_url, headers=download_headers, timeout=30)

with open("shop.png", "wb") as f:
    f.write(response.content)

file_size = os.path.getsize("shop.png")
print(f"File size downloaded: {file_size} bytes")

if file_size < 1000:
    raise ValueError("Download failed: Image file is too small or empty.")

# 3. Twitter Auth (OAuth 1.0a for media upload)
auth = tweepy.OAuth1UserHandler(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
api = tweepy.API(auth)

# Standard media upload
media = api.media_upload(filename="shop.png")
print(f"Media uploaded! Media ID: {media.media_id}")

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
