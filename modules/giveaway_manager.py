import asyncio

from .client import client
from .channel import join_channel, archive_channel, leave_channel, get_full_channel
from utils.pickling import update_local_channel_set, update_local_channel_map

class GiveawayManager:
    def __init__(self, channel_set, channel_map):
        self.channel_set = channel_set
        self.channel_map = channel_map
    
    # join channels required to participate
    async def join_participation(self, hash, giveaway):
        for channel_id in giveaway.channels:
            input_channel = await client.get_input_entity(channel_id)

            # join channel
            if not await join_channel(input_channel):
                await self.cancel_participation(hash)

            # archive channel
            await archive_channel(input_channel)

            # update local channel_set
            self.channel_set.add(input_channel.channel_id) # type: ignore
            update_local_channel_set()
    
    # cancel participation
    async def cancel_participation(self, hash):
        channels = self.channel_map[hash][0]
        for channel_id in channels:
            try:
                input_channel = await client.get_input_entity(channel_id)
                await leave_channel(input_channel) # type: ignore
                await asyncio.sleep(1)
            except Exception as e:
                # rarely gonna happen but just in case
                print("Error leaving channel:", e)

        self.channel_set.difference_update(channels)
        update_local_channel_set()
        del self.channel_map[hash]
        update_local_channel_map()
        
        
    async def set_update_hash(self, hash, channels, until_date, quantity):
        member_counts = []
        
        # get updated channel details
        for channel_id in channels:
            input_channel = await client.get_input_entity(channel_id)
            full_channel = await get_full_channel(input_channel) # type: ignore
            
            # if banned or channel in accessable
            if not full_channel:
                if hash in self.channel_map and self.channel_map[hash] != []:
                    print("You are banned from one of the channel")
                    await self.cancel_participation(hash)
                else:
                    print("Channel inacceaible")
                return False
            
            member_counts.append(full_channel.full_chat.participants_count) # type: ignore
            print("Member count: ", full_channel.full_chat.participants_count) # type: ignore
        
        # calculate participants and gift ratio
        participants = min(member_counts)
        gift_ratio = participants / quantity
        print("Participants to Gift ratio: ", gift_ratio)
        
        # Add hash to channel_map
        self.channel_map[hash] = [channels, until_date, quantity, participants, gift_ratio]
        update_local_channel_map()
        
        return self.channel_map[hash]

    # Evaluate giveaway is worth participating
    async def eval_giveaway(self, hash, chance_bound):
        gift_ratio = self.channel_map[hash][4]
        
        if gift_ratio > chance_bound:
            if hash in self.channel_map:
                print("Cancelling participation...")
                await self.cancel_participation(hash)
            
            print("Ain't No way you winnin this 💀")
            print(f"Gift ratio is more than {chance_bound}")
            print("×××××××××××××××××××××××××××××")
            return False
        
        return True