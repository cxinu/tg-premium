import os, dotenv, pickle, asyncio, time
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaGiveaway, InputReplyToMessage
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import SendMessageRequest


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

# Cancel Participation
async def cancel_participation(hash):
    channels = channel_map[hash][0]
    for channel_id in channels:
        try:
            input_channel = await client.get_input_entity(channel_id)
            await client(LeaveChannelRequest(input_channel)) # type: ignore
            await asyncio.sleep(1)
        except Exception as e:
            # rarely gonna happen but just in case
            print("Error leaving channel:", e)

        channel_set.difference_update(channels)
        del channel_map[hash]
        with open(set_file, 'wb') as f:
            pickle.dump(channel_set, f)
        with open(hash_file, 'wb') as f:
            pickle.dump(channel_map, f)
        
        
# Set or Update hash data
async def set_update_hash(hash, channels, until_date, quantity):
    member_counts = []
    for channel_id in channels:
        try:
            input_channel = await client.get_input_entity(channel_id)
            full_channel = await client(GetFullChannelRequest(input_channel)) # type: ignore
        except Exception as e:
            # Probably banned or private channel
            print("Error getting full channel:", e)
            print("×××××××××××××××××××××××××××××")
            
            if hash in channel_map:
                await cancel_participation(hash)
            return
        
        member_counts.append(full_channel.full_chat.participants_count) # type: ignore
        print("Member count: ", full_channel.full_chat.participants_count) # type: ignore
    
    participants = min(member_counts)
    gift_ratio = participants / quantity
    print("Participants to Gift ratio: ", gift_ratio)
    
    
    # If gift ratio is more than 10k, It's not worth participating
    if gift_ratio > 10000:
        print("Gift ratio is more than 10k")
        print("×××××××××××××××××××××××××××××")
        
        if hash in channel_map:
            await cancel_participation(hash)
        return
    
    # Add hash to channel_map
    channel_map[hash] = [channels, until_date, quantity, participants, gift_ratio]

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

    print("Link to giveaway: ", f"https://t.me/c/{hash}")
    print("Quantity of giveaway: ", giveaway.quantity)
    print("Time until ends: ", giveaway.until_date)
    
    # Evaluate chances and cofirm participation by adding hash
    await set_update_hash(hash, giveaway.channels, giveaway.until_date, giveaway.quantity)
    
    with open(hash_file, 'wb') as f:
        pickle.dump(channel_map, f)
    
    
    # Notify user about participation by replying to a message in another chat
    participants = channel_map[hash][3]
    gift_ratio = channel_map[hash][4]
    channel = await client.get_input_entity(event.chat_id)
    input_reply = InputReplyToMessage(event.message.id, reply_to_peer_id=channel)
    await client(SendMessageRequest(tg_premium_channel, f"Giveaway Alert: Participating with Quantity: {giveaway.quantity} Minimum Participants: {participants}, ratio: {gift_ratio}", reply_to=input_reply))


    # Participate in the giveaway
    for channel_id in giveaway.channels:
        input_channel = await client.get_input_entity(channel_id)
        
        # join channel (Archived), *move to a shared folder
        try:
            await client(JoinChannelRequest(input_channel)) # type: ignore
        except Exception as e:
            print("Error joining channel:", e)
            print("×××××××××××××××××××××××××××××")

        await client.edit_folder(input_channel, 1)
        
        # update local channel_set
        channel_set.add(input_channel.channel_id) # type: ignore
        with open(set_file, 'wb') as f:
            pickle.dump(channel_set, f)
    
    print("-----------------------------")


async def main():
    while True:
        print("------ Bot is running -------")
        for hash in list(channel_map.keys()):
            channels, until_date, quantity, participants, gift_ratio = channel_map[hash]
            if time.time() > until_date + (60 * 60):
                print("Giveaway ended: ", f"https://t.me/c/{hash}")
                print("Participants: ", participants)
                print("Gift ratio: ", gift_ratio)
                
                # Leave channel
                await cancel_participation(hash)
            else:
                print("Giveaway still running: ", f"https://t.me/c/{hash}")
                
                # Update hash data
                await set_update_hash(hash, channels, until_date, quantity)
                print("Participants: ", participants)
                print("Gift ratio: ", gift_ratio)
            
        await asyncio.sleep(6 * 60 * 60)  # Sleep for 6 hours



async def run_main_and_until_disconnected():
    await asyncio.gather(
        main(),
        client.run_until_disconnected() # type: ignore
    ) # type: ignore

with client:
    client.loop.run_until_complete(run_main_and_until_disconnected())