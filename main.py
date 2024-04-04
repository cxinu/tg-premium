import os, dotenv, asyncio
from typing import List

from datetime import datetime, timedelta, timezone
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaGiveaway, InputReplyToMessage
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import SendMessageRequest

# local imports
from utils.pickling import initialize_channels, update_local_channel_set, update_local_channel_map
from modules.giveaway_manager import GiveawayManager
from modules.client import client



channel_set, channel_map = initialize_channels()
tg_premium_channel_id = 2082273663
chance_bound = 10000


# Initialize Giveaway Manager
giveaway_manager = GiveawayManager(channel_set, channel_map)

# Main Event handler
@client.on(events.NewMessage(chats=channel_set))
async def handle_new_message(event):
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
    
    if not await giveaway_manager.set_update_hash(hash, giveaway.channels, giveaway.until_date, giveaway.quantity):
        return
    
    worth_participating = await giveaway_manager.eval_giveaway(hash, chance_bound)
    if not worth_participating:
        print("Not worth participating")
        return
    
    # Join channels Adds hash to channel_map
    await giveaway_manager.join_participation(hash, giveaway)
    
    # Notify user about participation by replying to a message in another chat
    tg_premium_channel = await client.get_input_entity(tg_premium_channel_id)
    participants = channel_map[hash][3]
    gift_ratio = channel_map[hash][4]
    
    channel = await client.get_input_entity(event.chat_id)
    input_reply = InputReplyToMessage(event.message.id, reply_to_peer_id=channel)
    await client(SendMessageRequest(tg_premium_channel, f"Giveaway Alert: Participating with Quantity: {giveaway.quantity} Minimum Participants: {participants}, ratio: {gift_ratio}", reply_to=input_reply))


    print("-----------------------------")


# Manage Current Giveaways
async def main():
    while True:
        print("- - - -Bot is running- - - -")
        # for hash in list(channel_map.keys()):
        #     print("----------------------------")
        #     print(f"hash: {hash}")
        #     print(f"Channels: {channel_map[hash][0]}")
        #     print(f"Until date: {channel_map[hash][1]}")
        #     print(f"Quantity: {channel_map[hash][2]}")
        #     print(f"Participants: {channel_map[hash][3]}")
        #     print(f"Gift ratio: {channel_map[hash][4]}")
        for hash in list(channel_map.keys()):
            channels, until_date, quantity, participants, gift_ratio = channel_map[hash]
            if datetime.now(timezone.utc) > until_date + timedelta(hours=1):
                print(" x x x x x x x x x x x x x x")
                print("Giveaway ended: ", f"https://t.me/c/{hash}")
                print(f"Channels: ", channels)
                print(f"Until date: ", until_date)
                print(f"Quantity: ", quantity)
                print("Participants: ", participants)
                print("Gift ratio: ", gift_ratio)
                
                # Leave channel
                await giveaway_manager.cancel_participation(hash)
            else:
                print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
                print("Giveaway still running: ", f"https://t.me/c/{hash}")
                
                # Update hash data
                await giveaway_manager.eval_giveaway(hash, chance_bound)
                print(f"Channels: ", channels)
                print(f"Until date: ", until_date)
                print(f"Quantity: ", quantity)
                print("Participants: ", participants)
                print("Gift ratio: ", gift_ratio)
        
        # print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
        print("+ + + + + + + + + + + + + + +")
        await asyncio.sleep(60 * 60)  # 1 hours



async def run_main_and_until_disconnected():
    await asyncio.gather(
        main(),
        client.run_until_disconnected() # type: ignore
    ) # type: ignore

with client:
    client.loop.run_until_complete(run_main_and_until_disconnected())