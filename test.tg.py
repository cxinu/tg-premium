# ------------------------------------------------
# This File is for testing telethon api & Project planning

# TODO:
# [x] Implement Hash map Data structure to store unique giveaways
# [x] Test if still can join channel after leaving: if one leaves no NewMessage Updates are returned
# [x] Auto Leave: when giveaway ends or no longer a participant Auto Leave the channel, del hash, remove from channel_set
# 
# Implement Logging
# Implement utils package
# Deploy bot: up and running on digital Ocial (github actions?, auto deploy?, docker container?)
# Implement Adding chats to custom folders and create new folder if limit reached
# Get a real database (firebase, supabase?) for storing hash and channel_set
# ------------------------------------------------

# Test:
import os
import dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest, GetSendAsRequest
from telethon.tl.functions.messages import SendMediaRequest


dotenv.load_dotenv()
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient('jackP', api_id, api_hash)

# Media Archived: 1506456927

@client.on(events.NewMessage(chats=2130678806))
async def handle_new_message(event):
    pass

async def main():
    channel = await client.get_input_entity(2130678806)
    print(channel.stringify())

client.start()
client.loop.run_until_complete(main())