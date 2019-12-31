# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import SyncConsumer
from channels.db import database_sync_to_async
import json
from .scraper import scrape
import threading

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'scrape_request',
                'title': message
            }
        )

    # Receive message from room group
    async def scrape_request(self, event):
        title = event['title']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': title + ' started in the background.'
        }))

        

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('echo',self.channel_name) 
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('echo',self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Send message to room group
        await self.channel_layer.group_send(
            'echo',
            {
                'type': 'echo_request',
                'yodle': text_data
            }
        )

    # Receive message from room group
    async def echo_request(self, event):
        yodle = event['yodle']
        # Send message to WebSocket
        await self.send(text_data=yodle)
