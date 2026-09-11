import os
import requests
import tweepy

# 1. Keys from GitHub Secrets
consumer_key = os.environ["X_API_KEY"]
consumer_secret = os.environ["X_API_SECRET"]
access_token = os.environ["X_ACCESS_TOKEN"]
access_token_secret = os.environ["X_ACCESS_TOKEN_SECRET"]
fn_key = os.environ["FN_API_KEY"]

# 2. Download Fortnite Shop Image
shop_url = "https://fortnite-api.com/v2/shop"
headers = {"Authorization": fn_key}
res = requests.get(shop_url, headers=headers).json()

img_url = res["data"]["composite"]
img_data = requests.get(img_url).content

with open("shop.png", "wb") as f:
    f.write(img_data)

# 3. Twitter Login
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)
api_v1 = tweepy.API(auth)
client_v2 = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
)

# 4. Upload & Tweet
media = api_v1.media_upload("shop.png")

caption = """Fortnite Item Shop Update! 🛒🔥

#Fortnite #ItemShop #FortniteItemShop"""

client_v2.create_tweet(text=caption, media_ids=[media.media_id])
print("Successfully posted to X!")
