#!/usr/bin/env python3
"""
Telegram message listener that launches commands
Usage::
    ./mthook.py api_id api_hash session "chat_id,command,regex" "chat_id,command,regex" ...
"""

import re
import requests
import subprocess
import sys
from datetime import datetime
from telethon import TelegramClient,events

async def main():
    await client.start()

    filters = {}

    for arg in sys.argv[4:]:
        vals = arg.split(',')
        reg = re.compile(vals[2])
        filters[vals[0]] = {'hook': vals[1], 'regex': reg}

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

        hook = filter['hook']
        if hook.startswith('http'):
            args = []
            for i in range (len(match.groups())):
                args.append(match.group(i+1))
            url = filter['hook']+','.join(args)
            print(datetime.now().time(), url)
            requests.get(url)
        else:
            args = [filter['hook']]
            for i in range (len(match.groups())):
                args.append(match.group(i+1))
            
            print(datetime.now().time(),' '.join(args))
            subprocess.run(args)

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
        print(datetime.now().time(), 'mthook started')
        client.run_until_disconnected()