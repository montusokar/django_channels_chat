from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from chat.models import User
from chat.models import Message
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def init_chat(self, data):
        print(data)
        username = data['username']
        content = {
            'command': 'init_chat'
        }
        content['success'] = 'Chatting success with username : ' + username
        await self.send(text_data=json.dumps(content))

    async def new_message(self, text_data):
        message = text_data['text']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    commands = {
        'init_chat': init_chat,
        'new_message': new_message
    }

    async def connect(self):

        self.room_name = 'room'
        self.room_group_name = 'chat_' + self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        json_data = json.loads(text_data)
        print(json_data)
        await self.commands[json_data['command']](self, json_data)

    # Receive message from room group
    async def chat_message(self, event):
        content = {
            'command': 'new_message'
        }
        content['message'] = event['message']
        await self.send(text_data=json.dumps(content))
