import pickle
import os

channel_set = set()
channel_map = {}
set_file = 'channel_set.pkl'
hash_file = 'channel_map.pkl'


# set_file & hash_file initialization
def initialize_channels():
    global channel_set, channel_map
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
    
    return channel_set, channel_map

def update_channel_set():
    global channel_set
    with open(set_file, 'wb') as f:
        pickle.dump(channel_set, f)
    return channel_set

def update_channel_map():
    global channel_map
    with open(hash_file, 'wb') as f:
        pickle.dump(channel_map, f)
    return channel_map