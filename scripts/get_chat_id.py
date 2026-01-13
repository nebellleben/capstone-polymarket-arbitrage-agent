#!/usr/bin/env python3
"""Get your Telegram Chat ID."""

import requests
import json

BOT_TOKEN = "8307798910:AAHnlKluqK92AVmfP-gEySC7DRNKtOBAHrk"

print("=" * 60)
print("Finding Your Telegram Chat ID")
print("=" * 60)
print()
print("Step 1: Start a chat with your bot")
print("  1. Open Telegram")
print("  2. Search for your bot (@polymarb_alert_bot or your bot's username)")
print("  3. Click 'Start' or send /start")
print()
print("Step 2: Press Enter to check for your Chat ID...")
input()

print()
print("Checking for updates...")
print()

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
data = response.json()

if data.get("ok"):
    results = data.get("result", [])

    if not results:
        print("❌ No updates found!")
        print()
        print("Please make sure you:")
        print("  1. Have started a chat with your bot (sent /start)")
        print("  2. Have actually sent a message to the bot")
        print()
        print("Then run this script again.")
    else:
        print("✅ Found updates! Here are the chat IDs:")
        print()

        chat_ids = set()
        for update in results:
            message = update.get("message", {})
            chat = message.get("chat", {})

            chat_id = chat.get("id")
            chat_type = chat.get("type")
            chat_title = chat.get("title", chat.get("first_name", "Unknown"))

            if chat_id:
                chat_ids.add(chat_id)
                print(f"  Chat ID: {chat_id}")
                print(f"  Type: {chat_type}")
                print(f"  Name: {chat_title}")
                print()

        if chat_ids:
            print("=" * 60)
            print("YOUR CHAT ID(S):")
            print("=" * 60)
            for cid in chat_ids:
                print(f"  {cid}")
            print()
            print("Use the numeric Chat ID in your .env file!")
else:
    print("❌ Error fetching updates")
    print(json.dumps(data, indent=2))
