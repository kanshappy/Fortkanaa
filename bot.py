import os
import requests
import tweepy

# 1. Keys from GitHub Secrets
consumer_key = os.environ["X_API_KEY"]
consumer_secret = os.environ["X_API_SECRET"]
access_token = os.environ["X_ACCESS_TOKEN"]
access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"]
fn_key = os.environ["FN_API_KEY"]

# 2. Daily Fortnite Shop Image Fetch & Download
shop_api = "https://fortnite-api.com/v2/shop"
headers = {"Authorization": fn_key}
res = requests.get(shop_api, headers=headers).json()

# Composite image or fallback verified store graphic
img_url = res.get("data", {}).get("composite")
if not img_url:
    img_url = "https://media.fortniteapi.io/images/shop/en/full_shop.png"

# User-Agent header serthu pure image binary download seithal
img_res = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
with open("shop.png", "wb") as f:
    f.write(img_res.content)

# 3. Twitter API Login
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)
api_v1 = tweepy.API(auth)
client_v2 = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# 4. Upload & Tweet
media = api_v1.media_upload(filename="shop.png")

caption = """Fortnite Item Shop Update! 🛒🔥

#Fortnite #ItemShop #FortniteItemShop"""

client_v2.create_tweet(text=caption, media_ids=[media.media_id])
print("Successfully posted to X!")
