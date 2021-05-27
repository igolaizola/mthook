#!/usr/bin/env python3
"""
Telegram message listener that launches commands
Usage::
    ./mthook.py api_id api_hash session "chat_id,script,regex" "chat_id,script,regex" ...
"""

import asyncio
import re
import subprocess
import sys

from telethon import TelegramClient,events

if len(sys.argv) == 2 and sys.argv[1] == 'version':
    print('1.21.1')
    exit()

if len(sys.argv) < 5:
    print('Usage mthook.py api_id api_hash session "chat_id,script,regex" "chat_id,script,regex" ...')
    exit()

# values from my.telegram.org
api_id = sys.argv[1]
api_hash = sys.argv[2]
client = TelegramClient(sys.argv[3], api_id, api_hash)

client.start()

filters = {}

for arg in sys.argv[4:]:
    vals = arg.split(',')
    reg = re.compile(vals[2])
    filters[vals[0]] = {'cmd': vals[1], 'regex': reg}

@client.on(events.NewMessage(pattern='.+'))
async def handler(event):
    if not hasattr(event, 'message'):
        return
    id = ''
    if hasattr(event.message.peer_id, 'channel_id'):
        id = str(event.message.peer_id.channel_id)
    elif hasattr(event.message.peer_id, 'user_id'):
        id = str(event.message.peer_id.user_id)
    elif hasattr(event.message.peer_id, 'chat_id'):
        id = str(event.message.peer_id.chat_id)
    else:
        return

    if not id in filters:
        return
    
    filter = filters[id]
    match = filter['regex'].search(event.message.message)
    if match is None:
        return

    args = [filter['cmd']]
    for i in range (len(match.groups())+1):
        args.append(match.group(i))
    
    subprocess.run(args)

client.run_until_disconnected()
