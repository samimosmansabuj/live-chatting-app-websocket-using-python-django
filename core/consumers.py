import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message, Attachment, CustomOffer, User
from django.core.exceptions import ObjectDoesNotExist

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return
        
        self.roomUUID = self.scope['url_route']['kwargs']['roomUUID']
        self.room_group_name = f'chat_{self.roomUUID}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    
    @database_sync_to_async
    def current_user_min(self):
        user = self.scope["user"]
        profile_url = ""
        return {'id': user.id, 'username': user.username, 'profile': profile_url}
    
    async def delete_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id, room_uuid=self.roomUUID)
            message.delete()
        except Message.DoesNotExist:
            return None
        
        payload = {
            "type": "chat_message",
            "msg_type": "chat_message_deleted",
            "message_id": message_id
        }
        await self.channel_layer.group_send(
            self.room_group_name, payload
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data or {})
        msg_type = (data.get("type") or "text").strip()
        message = (data.get("message") or "").strip()
        attachment = data.get("attachment") # {url, mime, name, size}
        offer = data.get("offer")
        
        if msg_type == "delete":
            message_id = data.get("message_id")
            payload = {
                "type": "chat_message",
                "msg_type": "delete",
                "message_id": message_id
            }
        elif msg_type == "text":
            if not message:
                return
            ok = await self.save_message(message)
            if not ok:
                return
            payload = {
                "type": "chat_message",
                "msg_type": "text",
                "message": message,
                "sender": ok["username"],
                "sender_id": ok["id"],
                "sender_profile": "",
                # "sender_profile": self._abs_url(ok["profile"]),
            }
        elif msg_type in ("image", "video", "audio", "file"):
            if not (attachment and isinstance(attachment, dict) and attachment.get("url")):
                return
            ok = await self.current_user_min()
            payload = {
                'type': 'chat_message',
                'msg_type': msg_type,
                'message': message,
                'attachment': {
                    'url': self._abs_url(attachment['url']),
                    'mime': attachment.get('mime', ''),
                    'name': attachment.get('name', ''),
                    'size': attachment.get('size', 0),
                },
                'sender': ok["username"],
                'sender_id': ok["id"],
                'sender_profile': self._abs_url(ok["profile"]),
            }
        elif msg_type == "offer":
            if not (offer and isinstance(offer, dict)):
                return
            ok = await self.current_user_min()
            payload = {
                'type': 'chat_message',
                'msg_type': msg_type,
                'offer': offer,  # contains id, title, amount_cents, currency, delivery_days, status
                'sender': ok["username"],
                'sender_id': ok["id"],
                'sender_profile': self._abs_url(ok["profile"]),
            }
        else:
            return
        
        await self.channel_layer.group_send(
            self.room_group_name, payload
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def save_message(self, message):
        user = self.scope["user"]
        try:
            room = ChatRoom.objects.get(uuid=self.roomUUID)
        except ObjectDoesNotExist:
            return False
        
        Message.objects.create(room=room, sender=user, content=message)
        profile_url = ''
        return {'id': user.id, 'username': user.username, 'profile': profile_url}
    
    
    def _http_scheme(self) -> str:
        headers = dict(self.scope.get("headers", []))
        xfproto = headers.get(b"x-forwarded-proto")
        if xfproto:
            proto = xfproto.decode("latin1").split(",")[0].strip().lower()
            return "https" if proto == "https" else "http"
        s = (self.scope.get("scheme") or "http").lower()
        if s in ("https", "wss"):
            return "https"
        return "http"

    def _host_with_port(self, scheme: str) -> str:
        """Prefer X-Forwarded-Host > Host > scope.server; drop default ports."""
        headers = dict(self.scope.get("headers", []))
        xfhost = headers.get(b"x-forwarded-host")
        host = (xfhost or headers.get(b"host") or b"").decode("latin1").strip()

        if not host:
            server = self.scope.get("server")  # e.g. ("127.0.0.1", 8000)
            if server:
                h, p = server[0], server[1]
                default = 443 if scheme == "https" else 80
                host = f"{h}:{p}" if (p and p != default) else h
            else:
                host = "localhost"
        return host

    def _abs_url(self, path: str) -> str:
        """Make absolute URL from /media/... using ASGI scope (scheme/host)."""
        if not path:
            return ""
        if isinstance(path, bytes):
            path = path.decode("utf-8", "ignore")
        if path.startswith(("http://", "https://")):
            return path
        scheme = self._http_scheme()
        host = self._host_with_port(scheme)
        if not path.startswith("/"):
            path = "/" + path
        return f"{scheme}://{host}{path}"