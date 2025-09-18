from telethon.sync import TelegramClient
import asyncio
import nest_asyncio
import sys
import traceback

# Apply nest_asyncio for Jupyter compatibility
nest_asyncio.apply()

# Telegram credentials
# Telegram credentials
api_id = YOUR_API_ID  # Replace with your API ID
api_hash = 'YOUR_API_HASH'  # Replace with your API hash
session_name = 'YOUR_SESSION_NAME'  # Replace with your session name

# Chat IDs
source_chat = -1002836877426  # Confession X
destination_chat = -1003038409258  # Confession channel

async def get_scan_limit():
    """Ask user for scan limit with 10-second timeout"""
    print("\n⏰ You have 10 seconds to specify how many messages to scan...")
    print("💡 Enter a number (e.g., 1000) or 'all' for entire history")
    
    try:
        # Get user input with timeout
        user_input = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, input, "📝 How many messages to scan? (default: all): "),
            timeout=10
        )
        
        if user_input.strip().lower() == 'all':
            return None  # None means scan all messages
        try:
            limit = int(user_input)
            return max(1, limit)  # Ensure at least 1 message
        except ValueError:
            print("⚠️ Invalid input. Scanning all messages.")
            return None
            
    except asyncio.TimeoutError:
        print("\n⏰ Timeout! Scanning all messages.")
        return None
    except Exception as e:
        print(f"⚠️ Error getting input: {e}. Scanning all messages.")
        return None

async def forward_pinned_messages():
    try:
        print("🚀 Starting Telegram client...")
        async with TelegramClient(session_name, api_id, api_hash) as client:
            # Verify connection
            print("🔒 Connected to Telegram successfully")
            me = await client.get_me()
            print(f"👤 Logged in as: {me.username if me.username else me.first_name}")

            # Get scan limit from user
            scan_limit = await get_scan_limit()
            
            # Get chat entities
            print(f"🔍 Resolving source chat (ID: {source_chat})...")
            src = await client.get_entity(source_chat)
            print(f"✅ Source chat found: {getattr(src, 'title', 'Unknown')}")
            
            print(f"🔍 Resolving destination chat (ID: {destination_chat})...")
            dest = await client.get_entity(destination_chat)
            print(f"✅ Destination chat found: {getattr(dest, 'title', 'Unknown')}")

            # Get pinned messages
            print(f"\n📌 Scanning for pinned messages...")
            pinned_messages = []
            total_scanned = 0
            
            # Determine total message count for progress tracking
            print("⏳ Determining total message count...")
            total_messages = await client.get_messages(src, limit=1)
            if total_messages and hasattr(total_messages[0], 'id'):
                total_count = total_messages[0].id
                print(f"ℹ️ Approximately {total_count} messages in chat")
            else:
                total_count = 0
                print("⚠️ Could not determine total message count")
            
            # Scan messages with user-specified limit
            limit_text = f"first {scan_limit}" if scan_limit else "all"
            print(f"🔍 Scanning {limit_text} messages...")
            
            async for message in client.iter_messages(src, limit=scan_limit):
                total_scanned += 1
                
                # Show progress every 100 messages
                if total_scanned % 100 == 0:
                    if scan_limit:
                        progress = (total_scanned / scan_limit) * 100
                        print(f"📊 Scanned {total_scanned}/{scan_limit} messages ({progress:.1f}%)")
                    elif total_count > 0:
                        progress = (total_scanned / total_count) * 100
                        print(f"📊 Scanned {total_scanned}/{total_count} messages ({progress:.1f}%)")
                    else:
                        print(f"📊 Scanned {total_scanned} messages")
                
                if hasattr(message, 'pinned') and message.pinned:
                    print(f"✅ Found pinned message (ID: {message.id}, Date: {message.date})")
                    pinned_messages.append(message)
            
            # Sort by date (oldest first) to maintain chronological order
            pinned_messages.sort(key=lambda x: x.date)
            
            if not pinned_messages:
                print("❌ No pinned messages found. This could be because:")
                print("   - The chat doesn't have any pinned messages")
                print("   - Your account doesn't have permission to view pinned messages")
                return
                
            print(f"✅ Found {len(pinned_messages)} pinned messages")

            # Forward messages in chronological order
            print(f"\n⏳ Forwarding {len(pinned_messages)} messages to destination...")
            for i, msg in enumerate(pinned_messages):
                try:
                    print(f"\n🔄 Processing message {i+1}/{len(pinned_messages)} (ID: {msg.id}, Date: {msg.date})")
                    content_preview = msg.text[:100] + '...' if msg.text and len(msg.text) > 100 else (msg.text or "Media message")
                    print(f"📝 Content preview: {content_preview}")
                    await client.forward_messages(dest, msg)
                    print(f"✅ Successfully forwarded message {i+1}")
                except Exception as e:
                    print(f"⚠️ Failed to forward message {msg.id}: {str(e)}")
                    print(f"🔧 Continuing with next message...")

            print(f"\n🎉 Successfully forwarded {len(pinned_messages)} pinned messages!")

    except Exception as e:
        print("\n‼️ CRITICAL ERROR ‼️")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        print("\n🚨 Traceback:")
        traceback.print_exc()
        sys.exit(1)

# Run in Jupyter environment
if __name__ == "__main__":
    print("="*50)
    print("🏁 STARTING PINNED MESSAGE FORWARDER")
    print("="*50)
    
    try:
        # For Jupyter
        await forward_pinned_messages()
    except:
        # For standard Python execution
        asyncio.run(forward_pinned_messages())
    
    print("="*50)
    print("🛑 PROGRAM EXECUTION COMPLETE")
    print("="*50)
