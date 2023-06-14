#!/usr/bin/env python

# WS server example

#https://websockets.readthedocs.io/en/stable/intro.html
#の最後にあるように，websocketは面倒な作業を背後で自動でやってくれる．
#micropythonにはそのような物がない．

import asyncio
import websockets

async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

start_server = websockets.serve(hello, "10.0.1.9", 8765)
# start_server = websockets.serve(hello, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()