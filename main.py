import os
import dotenv
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaGiveaway
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputReplyToMessage
import pickle
import asyncio

lock = asyncio.Lock()
dotenv.load_dotenv()

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
client = TelegramClient('jackP', api_id, api_hash)

channel_set = set()
channel_map = {}
set_file = 'channel_set.pkl'
hash_file = 'channel_map.pkl'
tg_premium_channel_id = 2082273663


# set_file & hash_file initialization
if not os.path.exists(set_file):
    with open(set_file, 'wb') as f:
        channel_set.update([2082273663, 2130678806, 2117422267, 2005330850, 2013815665])
        pickle.dump(channel_set, f)
else:
    with open(set_file, 'rb') as f:
        channel_set = pickle.load(f)

if not os.path.exists(hash_file):
    with open(hash_file, 'wb') as f:
        pickle.dump(channel_map, f)
else:
    with open(hash_file, 'rb') as f:
        channel_map = pickle.load(f)

# Main Event handler
@client.on(events.NewMessage(chats=channel_set))
async def handle_new_message(event):
    tg_premium_channel = await client.get_input_entity(tg_premium_channel_id)
    giveaway = event.message.media
    
    # message type is giveaway and no cournty restriction
    if not isinstance(giveaway, MessageMediaGiveaway):
        return
    if giveaway.countries_iso2 and 'IN' not in giveaway.countries_iso2:
        return
    
    # check if already participating in the giveaway
    og_channel_id = event.message.fwd_from.from_id.channel_id
    og_message_id = event.message.fwd_from.channel_post
    hash = f"{og_channel_id}/{og_message_id}"
    if hash in channel_map:
        return

    # check if the giveaway is worth participating
    print("Quantity of giveaway: ", giveaway.quantity)
    member_counts = []
    for channel_id in giveaway.channels:
        input_channel = await client.get_input_entity(channel_id)
        try:
            full_channel = await client(GetFullChannelRequest(input_channel))
        except Exception as e:
            print("Error getting full channel:", e)
            print("×××××××××××××××××××××××××××××")
            return
        
        member_counts.append(full_channel.full_chat.participants_count)
        print("Member count: ", full_channel.full_chat.participants_count)
    
    participants = min(member_counts)
    gift_ratio = participants / giveaway.quantity
    print("Participants to Gift ratio: ", gift_ratio)
    
    if gift_ratio > 10000:
        print("Gift ratio is more than 10k")
        print("×××××××××××××××××××××××××××××")
        return
    
    # Add hash to channel_map
    channel_map[hash] = [og_channel_id, og_message_id, giveaway.channels, giveaway.until_date, giveaway.quantity, participants, gift_ratio]
    
    with open(hash_file, 'wb') as f:
        pickle.dump(channel_map, f)
    
    # Notify the user about the giveaway by replying to a message in another chat of specific id
    channel = await client.get_input_entity(event.chat_id)
    input_reply = InputReplyToMessage(event.message.id, reply_to_peer_id=channel)
    await client(SendMessageRequest(tg_premium_channel, f"Giveaway Alert: Participating with Quantity: {giveaway.quantity} Minimum Participants: {participants}, ratio: {gift_ratio}", reply_to=input_reply))


    # Participate in the giveaway
    for channel_id in giveaway.channels:
        input_channel = await client.get_input_entity(channel_id)
        
        # join channel (Archived), *move to a shared folder
        try:
            await client(JoinChannelRequest(input_channel))
        except Exception as e:
            print("Error joining channel:", e)
            print("×××××××××××××××××××××××××××××")

        await client.edit_folder(input_channel, 1)
        
        # update local channel_set
        channel_set.add(input_channel.channel_id)
        with open(set_file, 'wb') as f:
            pickle.dump(channel_set, f)
    
    print("-----------------------------")
    # print(channel_set)
    # print(channel_map)
                

client.start()
client.run_until_disconnected()