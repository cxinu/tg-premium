import os
import dotenv
from telethon import TelegramClient

dotenv.load_dotenv()

# Replace the values below with your own API ID and API Hash
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']

client = TelegramClient('jackP', api_id, api_hash)


async def main():
    # Getting information about yourself
    me = await client.get_me()
    print(me.stringify())


with client:
    print('Running client...')
    client.loop.run_until_complete(main())