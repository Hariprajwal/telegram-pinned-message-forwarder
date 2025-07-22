from telethon.sync import TelegramClient
import asyncio
import nest_asyncio
import sys
import traceback
import os

# Apply nest_asyncio for environments like Jupyter or notebooks
nest_asyncio.apply()

# 🛡️ Read Telegram credentials from environment variables or .env file
api_id = int(os.getenv('API_ID', 'YOUR_API_ID'))
api_hash = os.getenv('API_HASH', 'YOUR_API_HASH')
session_name = os.getenv('SESSION_NAME', 'session')

# 📌 Replace with your source and destination chat IDs
source_chat = int(os.getenv('SOURCE_CHAT_ID', '-1001234567890'))
destination_chat = int(os.getenv('DESTINATION_CHAT_ID', '-1009876543210'))

async def forward_pinned_messages():
    try:
        print("🚀 Starting Telegram client...")
        async with TelegramClient(session_name, api_id, api_hash) as client:
            print("🔒 Connected to Telegram successfully")
            print(f"👤 Logged in as: {(await client.get_me()).username}")

            # Resolve chats
            src = await client.get_entity(source_chat)
            print(f"✅ Source chat found: {src.title}")
            dest = await client.get_entity(destination_chat)
            print(f"✅ Destination chat found: {dest.title}")

            # Search for pinned messages
            pinned_messages = []
            total_count = 0
            async for msg in client.iter_messages(src):
                total_count += 1
                if msg.pinned:
                    print(f"📌 Found pinned message (ID: {msg.id})")
                    pinned_messages.append(msg)

            print(f"\nℹ️ Total messages scanned: {total_count}")
            print(f"📌 Total pinned messages found: {len(pinned_messages)}")

            if not pinned_messages:
                print("❌ No pinned messages found.")
                return

            # Forward pinned messages
            print(f"\n⏳ Forwarding {len(pinned_messages)} messages to destination...")
            for i, msg in enumerate(reversed(pinned_messages)):
                try:
                    print(f"🔄 Forwarding message {i+1}/{len(pinned_messages)} (ID: {msg.id})")
                    await client.forward_messages(dest, msg)
                    print("✅ Message forwarded successfully")
                except Exception as e:
                    print(f"⚠️ Error forwarding message {msg.id}: {e}")

            print(f"\n🎉 All pinned messages forwarded successfully!")

    except Exception as e:
        print("\n‼️ CRITICAL ERROR ‼️")
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)

# Start the process
if __name__ == "__main__":
    print("="*50)
    print("🏁 STARTING PINNED MESSAGE FORWARDER")
    print("="*50)
    asyncio.run(forward_pinned_messages())
    print("="*50)
    print("🛑 PROGRAM EXECUTION COMPLETE")
    print("="*50)
