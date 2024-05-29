import re
import logging
import tweepy
import yt_dlp as youtube_dl
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram import InputFile
import telegram.ext.filters as filters
from telegram.ext import Application
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext import Application, ApplicationBuilder
from telegram import Update, InputMediaPhoto
import requests
import base64
import hashlib
import os

# Updated Twitter API v2 endpoint URL
API_URL = "https://api.x.com/2/"

# Twitter app credentials
CLIENT_ID = "ZmNkLXBkTlloX0JFaXVnNW0xclg6MTpjaQ"
CLIENT_SECRET = "dPaJ-nYPm5dKkzIa0fUD3LPlzqzIyGfEwqW-0tyGDJsSIDzf2n"
REDIRECT_URI = "https://web.telegram.org/k/#@mytwitmr_bot"  # Must match the one configured in your Twitter app settings
SCOPE = "read:users"  # Adjust based on your application's required scope

# Define your Telegram bot token and channel ID
TELEGRAM_BOT_TOKEN = "7429258149:AAGI3JvmNkODEKG_SXdq8aBYISsstittQB4"
CHANNEL_ID = "@mytwitmr_bot"

# Set up Tweepy for Twitter API v2
auth = tweepy.AppAuthHandler(CLIENT_ID,CLIENT_SECRET)
api = tweepy.API(auth)

def generate_code_verifier(length=64):
    # Generate a random string to be used as the code verifier
    return base64.urlsafe_b64encode(os.urandom(length)).decode().replace('=', '')

def generate_code_challenge(verifier):
    # Generate the code challenge from the code verifier using SHA256
    return hashlib.sha256(verifier.encode()).digest()

def get_access_token(code, code_verifier):
    # Exchange authorization code for access token
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Authorization": f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    access_token = response.json()["access_token"]

    return access_token

def get_x_post(tweet_id):
    # Fetch Twitter post by ID
    response = requests.get(API_URL + f"tweets/{tweet_id}")
    tweet_data = response.json()
    return tweet_data

def download_x_video(media_url):
    # Download video from Twitter URL
    response = requests.get(media_url)
    if response.status_code == 200:
        with open("video.mp4", "wb") as video_file:
            video_file.write(response.content)
        return "video.mp4"
    else:
        return None

def handle_x_thread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    x_thread_link = re.search(r'(https?://x\.com/[^\s]+/status/\d+)', message)

    if twitter_thread_link:
        url = twitter_thread_link.group(0)
        tweet_id = url.split('/')[-1]
        tweet_data = get_twitter_post(tweet_id)
        tweet_text = tweet_data['data']['text']
        update.message.reply_text(tweet_text)

        # Check if the tweet contains media (e.g., video)
        if 'media' in tweet_data['data']:
            media_url = tweet_data['data']['media'][0]['url']
            video_path = download_twitter_video(media_url)
            if video_path:
                with open(video_path, 'rb') as video:
                    context.bot.send_video(chat_id=CHANNEL_ID, video=video)
                os.remove(video_path)
            else:
                update.message.reply_text("Failed to download video.")
    else:
        update.message.reply_text('Please send a valid Twitter thread link.')

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_x_thread))

    application.run_polling()

if __name__ == "__main__":
    main()



