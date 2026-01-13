#!/usr/bin/env python3
"""
Simple script to find your Telegram Chat ID.
Run this, then send /start to your bot in Telegram.
"""

import requests
import time

BOT_TOKEN = "8307798910:AAHnlKluqK92AVmfP-gEySC7DRNKtOBAHrk"

print("=" * 70)
print("TELEGRAM CHAT ID FINDER")
print("=" * 70)
print()
print("Follow these steps:")
print()
print("1. Open Telegram on your phone or computer")
print("2. Search for your bot: @polymarb_alert_bot")
print("3. Click on the bot and send: /start")
print()
print("Once you've done that, this script will find your Chat ID.")
print()
print("Waiting for you to send /start to your bot...")
print("(Checking every 3 seconds)")
print()

seen_ids = set()

try:
    while True:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        response = requests.get(url)
        data = response.json()

        if data.get("ok"):
            results = data.get("result", [])

            for update in results:
                message = update.get("message", {})
                chat = message.get("chat", {})

                chat_id = chat.get("id")
                chat_type = chat.get("type")
                chat_name = chat.get("title", chat.get("first_name", chat.get("username", "Unknown")))

                if chat_id and chat_id not in seen_ids:
                    seen_ids.add(chat_id)

                    print("=" * 70)
                    print("✅ FOUND YOUR CHAT ID!")
                    print("=" * 70)
                    print()
                    print(f"Chat ID: {chat_id}")
                    print(f"Type: {chat_type}")
                    print(f"Name: {chat_name}")
                    print()

                    if chat_type == "private":
                        print("This is your personal Chat ID (perfect for receiving alerts!)")
                    elif chat_type == "group":
                        print("This is a group Chat ID")
                    elif chat_type == "channel":
                        print("This is a channel Chat ID")
                    elif chat_type == "supergroup":
                        print("This is a supergroup Chat ID")

                    print()
                    print("Copy this number and use it as TELEGRAM_CHAT_ID in your .env file")
                    print()
                    print("Press Ctrl+C to exit")
                    print()

        time.sleep(3)

except KeyboardInterrupt:
    print()
    print("Done! Use the Chat ID shown above in your .env file.")
