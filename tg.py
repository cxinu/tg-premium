import os
import dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest

# File for testing telethon

dotenv.load_dotenv()
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient('jackP', api_id, api_hash)

async def main():
    # me  = await client.get_me()
    # print(me.stringify())
    
    # in_me = await client.get_input_entity(-1002082273663)
    channel = await client.get_input_entity(-1002130678806)
    full_channel = await client(GetFullChannelRequest(channel)) # type: ignore
    print(full_channel.full_chat.participants_count)
    # print(channel.stringify())
    
    

client.start()
client.loop.run_until_complete(main())