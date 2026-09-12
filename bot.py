import os
import requests
import tweepy

# 1. Credentials
consumer_key = os.environ["X_API_KEY"].strip()
consumer_secret = os.environ["X_API_SECRET"].strip()
access_token = os.environ["X_ACCESS_TOKEN"].strip()
access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"].strip()
fn_key = os.environ.get("FN_API_KEY", "").strip()

# 2. Download Real Store Composite Image
url = "https://fortnite-api.com/v2/shop"
headers = {"Authorization": fn_key} if fn_key else {}
res = requests.get(url, headers=headers).json()

# Extract direct composite image
img_url = None
if "data" in res and isinstance(res["data"], dict):
    img_url = res["data"].get("composite")

# Fallback direct high-res shop image
if not img_url:
    img_url = "https://media.fortniteapi.io/images/shop/en/full_shop.png"

response = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
if response.status_code == 200 and len(response.content) > 1000:
    with open("shop.png", "wb") as f:
        f.write(response.content)
else:
    raise Exception("Image download failed or invalid content size!")

# 3. Twitter Auth (OAuth 1.0a User Context for Media Upload)
auth = tweepy.OAuth1UserHandler(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
api = tweepy.API(auth)

# Upload media with explicit mime type
media = api.media_upload(filename="shop.png")

# 4. Tweet Post via v2 Client
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
