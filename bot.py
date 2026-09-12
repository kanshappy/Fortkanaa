import os
import requests
import tweepy

# 1. Credentials
consumer_key = os.environ["X_API_KEY"].strip()
consumer_secret = os.environ["X_API_SECRET"].strip()
access_token = os.environ["X_ACCESS_TOKEN"].strip()
access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"].strip()
fn_key = os.environ.get("FN_API_KEY", "").strip()

# 2. Fetch Shop Data from Fortnite-API.com
headers = {"Authorization": fn_key} if fn_key else {}
api_url = "https://fortnite-api.com/v2/shop"

img_url = None
try:
    r = requests.get(api_url, headers=headers, timeout=15)
    data = r.json().get("data", {})
    
    # Priority 1: Composite store image
    img_url = data.get("composite")
    
    # Priority 2: Extract active shop banner
    if not img_url:
        entries = data.get("entries", [])
        if not entries:
            entries = data.get("featured", {}).get("entries", [])
        
        for item in entries:
            # Check render asset
            render = item.get("newDisplayAsset", {}).get("materialInstances", [{}])[0].get("images", {}).get("Background")
            if render:
                img_url = render
                break
            # Check direct item image
            sub_items = item.get("items", [])
            if sub_items:
                img_url = sub_items[0].get("images", {}).get("featured") or sub_items[0].get("images", {}).get("icon")
                if img_url:
                    break
except Exception as e:
    print(f"Error fetching API data: {e}")

# Working fallback image from official CDN
if not img_url:
    img_url = "https://fortnite-api.com/images/cosmetics/br/cid_515_athena_commando_m_barbecue/icon.png"

print(f"Downloading from: {img_url}")

# 3. Download Binary Image
headers_download = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
img_data = requests.get(img_url, headers=headers_download, timeout=20).content

with open("shop.png", "wb") as f:
    f.write(img_data)

file_size = os.path.getsize("shop.png")
print(f"Downloaded file size: {file_size} bytes")

# 4. Twitter Authentication & Upload
auth = tweepy.OAuth1UserHandler(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
api = tweepy.API(auth)
media = api.media_upload(filename="shop.png")

# 5. Tweet via v2 API
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
