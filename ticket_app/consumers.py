import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import *

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.ticket_id = self.scope["url_route"]["kwargs"]["ticket_id"]
        self.user = self.scope["user"]
        self.room_group_name = f"ticket_{self.ticket_id}"
        # self.user_inbox = f'inbox_{self.user.username}'
        
        ticket = Ticket.objects.get(id=self.ticket_id)

        if self.user == ticket.customer or self.user == ticket.agent:
            print(self.user)
            print('authenticated')
            if self.user.is_authenticated:
                
                print('authenticated2')

                async_to_sync(self.channel_layer.group_add)(
                        self.room_group_name,
                        self.channel_name, 
                )
                self.accept()
        else: 
            print('closing...')       
            self.close()
    def disconnect(self, close_code):
        
        if self.user.is_authenticated:
            
            # delete the user inbox for private messages
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name,
            )   

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
 
        

        if not self.user.is_authenticated:
            return

        
        # send private message to the target
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'private_message',
                'user': self.user.username,
                'message': message,
            }
        )
        ticket = Ticket.objects.get(id=self.ticket_id)

        Comment.objects.create(
            ticket = ticket,
            user = self.user,
            message = message
        )
 
        return 
    
    def private_message(self, event):
        self.send(text_data=json.dumps(event))

    
 