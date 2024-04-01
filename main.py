import os
import dotenv
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaGiveaway
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.custom.chatgetter import ChatGetter

dotenv.load_dotenv()
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
client = TelegramClient('jackP', api_id, api_hash)

@client.on(events.NewMessage(chats=('me', -1001506456927)))
async def handle_new_message(event):
    sender = await event.get_sender()
    if isinstance(event.message.media, MessageMediaGiveaway):
        giveaway = event.message.media
        
        if not giveaway.countries_iso2 or 'IN' in giveaway.countries_iso2:
            for channel_id in giveaway.channels:
                channel = await client.get_input_entity(channel_id)
                # Join chennel
                result = await client(JoinChannelRequest(channel))
                # Archive channel
                await client.edit_folder(channel, 1)
                
                

client.start()
client.run_until_disconnected()