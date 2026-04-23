import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.groups_to_join = []

        # Grupos específicos según el rol
        if getattr(self.user, "rol", "") == "ADMIN":
            self.groups_to_join.append("admin_feed")
        else:
            self.groups_to_join.append(f"user_{self.user.id}_feed")

        # Unirse a todos los grupos calculados
        for group in self.groups_to_join:
            await self.channel_layer.group_add(group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Abandonar los grupos al desconectarse
        if hasattr(self, "groups_to_join"):
            for group in self.groups_to_join:
                await self.channel_layer.group_discard(group, self.channel_name)

    # Manejadores de mensajes recibidos desde el channel layer (ej: en signals)
    async def send_notification(self, event):
        """
        Envía una notificación al cliente a través del WebSocket.
        """
        payload = event["payload"]
        await self.send(text_data=json.dumps(payload))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        # Unirse al grupo global de chat
        self.room_group_name = "global_chat"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action_type = data.get("type")

        # El guardado de mensajes reales va por la API REST.
        # Por WS solo rebotamos el evento de 'escribiendo...'
        if action_type == "typing_status":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_indicator",
                    "username": self.user.username,
                    "is_typing": data.get("is_typing", False)
                }
            )

    async def chat_message(self, event):
        # Recibe mensaje real de la API
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"]
        }))

    async def typing_indicator(self, event):
        # Rebota a los clientes
        await self.send(text_data=json.dumps({
            "type": "typing_status",
            "username": event["username"],
            "is_typing": event["is_typing"]
        }))
