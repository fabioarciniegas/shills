import asyncio
import websockets
import json

async def hello():
    async with websockets.connect(
            'ws://localhost:8000/ws/film_scrapping/') as websocket:

        await websocket.send(json.dumps({
            'film': 'a film.',
            'percentage': 'a percentage.'
        }))

        greeting = await websocket.recv()
        print(f"Received: {greeting}")

asyncio.get_event_loop().run_until_complete(hello())
asyncio.get_event_loop().run_until_complete(hello())
