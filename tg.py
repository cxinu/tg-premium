import os
import dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest, GetSendAsRequest
from telethon.tl.functions.messages import SendMediaRequest


# ------------------------------------------------
# This File is for testing telethon api & Project planning

# TODO:
# Implement Hash map Data structure to store unique giveaways
# Implement Adding chats to custom folders and create new folder if limit reached 
# Test if still can join channel after leaving
# Make this script upand running on digital Ocial (github actions?, auto deploy?, docker container?)
# ------------------------------------------------

dotenv.load_dotenv()
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient('jackP', api_id, api_hash)

# Media Archived: -1001506456927

@client.on(events.NewMessage(chats=-1002130678806))
async def handle_new_message(event):
    

async def main():
    channel = await client.get_input_entity(-1002130678806)
    
    
    
    

client.start()
client.loop.run_until_complete(main())