#!/usr/bin/env python3
"""
Telegram message listener that launches commands
Usage::
    ./mthook.py api_id api_hash session "chat_id,command,regex" "chat_id,command,regex" ...
"""

import asyncio
import re
import subprocess
import sys

from telethon import TelegramClient,events

async def main():
    await client.start()

    filters = {}

    for arg in sys.argv[5:]:
        vals = arg.split(',')
        reg = re.compile(vals[2])
        filters[vals[0]] = {'cmd': vals[1], 'regex': reg}

    log_id = int(sys.argv[4])
    await client.send_message(log_id, 'mthook started')

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
        for i in range (len(match.groups())):
            args.append(match.group(i+1))
        
        print(' '.join(args))
        subprocess.run(args)
        await client.send_message(log_id, ' '.join(args))

if len(sys.argv) == 2 and sys.argv[1] == 'version':
    print('1.21.1')
elif len(sys.argv) < 5:
    print('Usage mthook.py api_id api_hash session "chat_id,command,regex" "chat_id,command,regex" ...')
else:
    # values from my.telegram.org
    api_id = sys.argv[1]
    api_hash = sys.argv[2]
    client = TelegramClient(sys.argv[3], api_id, api_hash)
    with client:
        client.loop.run_until_complete(main())
        print('mthook started')
        client.run_until_disconnected()