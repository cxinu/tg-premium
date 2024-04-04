from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest, GetFullChannelRequest
from .client import client

async def join_channel(input_channel):
    try:
        await client(JoinChannelRequest(input_channel)) # type: ignore
        return True
    except Exception as e:
        print("Error joining channel:", e)
        print("×××××××××××××××××××××××××××××")
        return False

async def archive_channel(input_channel):
    await client.edit_folder(input_channel, 1)

async def leave_channel(input_channel):
    await client(LeaveChannelRequest(input_channel)) # type: ignore

async def get_full_channel(input_channel):
    try:
        return await client(GetFullChannelRequest(input_channel)) # type: ignore
    except Exception as e:
        # Probably banned (becomes private channel)
        print("Error getting full channel:", e)
        print("×××××××××××××××××××××××××××××")
        return False