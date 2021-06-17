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
from pyrogram import Client, filters

def handle(fs, message):
    id = ''
    if hasattr(message, 'chat') and hasattr(message.chat, 'username'):
        id = message.chat.username
    elif hasattr(message, 'chat') and hasattr(message.chat, 'id'):
        id = message.chat.id
    else:
        return
    
    if not id in fs:
        return

    filter = fs[id]
    match = filter['regex'].search(message.text)
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
    print('1.2.9')
elif len(sys.argv) < 5:
    print('Usage mthook.py api_id api_hash session "chat_id,command,regex" "chat_id,command,regex" ...')
else:
    # values from my.telegram.org
    api_id = sys.argv[1]
    api_hash = sys.argv[2]
    
    app = Client(sys.argv[3], api_id, api_hash)
    print(datetime.now().time(), 'mthook started')

    fs = {}
    for arg in sys.argv[4:]:
        vals = arg.split(',')
        reg = re.compile(vals[2])
        fs[vals[0]] = {'hook': vals[1], 'regex': reg}

    @app.on_message(filters.text)
    def onMessage(client, message):
        handle(fs, message)

    app.run()
