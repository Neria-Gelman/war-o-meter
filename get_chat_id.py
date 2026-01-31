#!/usr/bin/env python3
"""Get your Telegram chat ID by checking for recent messages to your bot."""

import json
import os
import urllib.request

from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
    exit(1)

url = f"https://api.telegram.org/bot{token}/getUpdates"

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode())

    if not data.get("ok"):
        print(f"ERROR: {data}")
        exit(1)

    updates = data.get("result", [])

    if not updates:
        print("No messages found.")
        print("\nTo get your chat ID:")
        print("1. Open Telegram and find your bot")
        print("2. Send /start or any message to your bot")
        print("3. Run this script again")
        exit(0)

    print("Recent chats with your bot:\n")
    seen = set()
    for update in updates:
        msg = update.get("message", {})
        chat = msg.get("chat", {})
        chat_id = chat.get("id")

        if chat_id and chat_id not in seen:
            seen.add(chat_id)
            chat_type = chat.get("type", "unknown")
            name = chat.get("first_name", "") or chat.get("title", "")
            username = chat.get("username", "")

            print(f"  Chat ID: {chat_id}")
            print(f"  Type: {chat_type}")
            print(f"  Name: {name}")
            if username:
                print(f"  Username: @{username}")
            print()

    print("-" * 40)
    print("Copy the Chat ID above into your .env file as TELEGRAM_CHAT_ID")

except Exception as e:
    print(f"ERROR: {e}")
