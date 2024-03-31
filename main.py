import os
import dotenv
from telethon import TelegramClient, events

dotenv.load_dotenv()

# Replace the values below with your own API ID and API Hash
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']

client = TelegramClient('jackP', api_id, api_hash)
client.start()

@client.on(events.NewMessage(chats=('me')))
async def handle_new_message(event):
    sender = await event.get_sender()
    print(f"New message from {sender.username}: {event.text}")

client.run_until_disconnected()