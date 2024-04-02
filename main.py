import os
import dotenv
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaGiveaway
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
import pickle


dotenv.load_dotenv()
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient('jackP', api_id, api_hash)

channel_set = set()
pkl_file = 'channel_set.pkl'

if not os.path.exists(pkl_file):
    with open(pkl_file, 'wb') as f:
        channel_set.add(-1002082273663)
        channel_set.add(-1002130678806)
        channel_set.add(-1002117422267)
        channel_set.add(-1002005330850)
        channel_set.add(-1002013815665)
        pickle.dump(channel_set, f)
else:
    with open(pkl_file, 'rb') as f:
        channel_set = pickle.load(f)
    

@client.on(events.NewMessage(chats=channel_set))
async def handle_new_message(event):
    giveaway = event.message.media
    
    # message type is giveaway and no cournty restriction
    if not isinstance(giveaway, MessageMediaGiveaway):
        return
    if giveaway.countries_iso2 and 'IN' not in giveaway.countries_iso2:
        return
    
    
    # check if the giveaway is worth participating
    print("Quantity of giveaway: ", giveaway.quantity)
    member_counts = []
    for channel_id in giveaway.channels:
        input_channel = await client.get_input_entity(channel_id)
        full_channel = await client(GetFullChannelRequest(input_channel))
        
        member_counts.append(full_channel.full_chat.participants_count)
        print("Member count: ", full_channel.full_chat.participants_count)
    
    gift_ratio = min(member_counts) / giveaway.quantity
    print("Participants to Gift ratio: ", gift_ratio)
    
    if gift_ratio > 10000:
        print("Gift ratio is more than 10k")
        return

    # Participate in the giveaway
    for channel_id in giveaway.channels:
        input_channel = await client.get_input_entity(channel_id)
        
        # join channel (Archived), *move to a shared folder
        await client(JoinChannelRequest(input_channel))
        await client.edit_folder(input_channel, 1)
        
        # update local channel_set
        channel_set.add(input_channel.channel_id)
        with open(pkl_file, 'wb') as f:
            pickle.dump(channel_set, f)
        print(channel_set)            
                

client.start()
client.run_until_disconnected()