# rps_app/consumers.py
import json
import logging
from collections import Counter
from datetime import timezone

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import ChatMessage, ChatRoom, MessageReaction, Student, Teacher

logger = logging.getLogger(__name__)
User = get_user_model()


# ==============================================
# CHAT CONSUMER (Room-specific) - FIXED
# ==============================================
class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.user = None

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user or not self.user.is_authenticated:
            logger.warning("Unauthenticated user tried to connect to chat")
            await self.close()
            return

        # Safely get room_name
        room_name = self.scope["url_route"]["kwargs"].get("room_name")
        if not room_name:
            logger.warning("No room_name provided")
            await self.close()
            return

        self.room_name = room_name
        self.room_group_name = self.room_name

        # Add to group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        logger.info(f"User {self.user.username} connected to chat room {self.room_group_name}")

        # Mark messages as seen and broadcast online status
        try:
            await self._mark_messages_seen()
            await self._broadcast_online_status(True)
        except Exception as e:
            logger.error(f"Error in connect post-accept: {e}")

    async def disconnect(self, close_code):
        """SAFE DISCONNECT - No more AttributeError"""
        try:
            if hasattr(self, 'room_group_name') and self.room_group_name:
                await self._broadcast_online_status(False)
                if hasattr(self, 'channel_name') and self.channel_name:
                    await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
                logger.info(f"User {self.user.username if self.user else 'unknown'} disconnected from {self.room_group_name}")
        except Exception as e:
            logger.error(f"Error in chat disconnect: {e}")

    # ------------------------------------------------------------------
    # Receive from WebSocket
    # ------------------------------------------------------------------
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            msg_type = data.get("type")

            if msg_type == "message":
                await self._handle_message(data)
            elif msg_type == "typing":
                await self._handle_typing(data["is_typing"])
            elif msg_type == "reaction":
                await self._handle_reaction(data)
            else:
                logger.warning(f"Unknown message type: {msg_type}")
        except Exception as e:
            logger.error(f"Error in receive: {e}")

    # ------------------------------------------------------------------
    # Handle incoming message
    # ------------------------------------------------------------------
    async def _handle_message(self, data):
        receiver_username = data.get("receiver_username")
        receiver = await self._get_user(receiver_username)
        if not receiver:
            logger.warning(f"Receiver {receiver_username} not found")
            return

        # Status: 1 if receiver is online, else 0
        receiver_online = await self._is_user_online_in_room(receiver)
        initial_status = 1 if receiver_online else 0

        msg = await self._create_message(
            sender=self.user,
            receiver=receiver,
            message=data.get("message"),
            file_path=data.get("file_path"),
            initial_status=initial_status
        )

        # Update ChatRoom
        await self._update_chat_room_last_message(msg)

        # Broadcast to chat room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_id": msg.id,
                "message": msg.message or "",
                "sender_username": self.user.username,
                "file_url": msg.file.url if msg.file else None,
                "file_name": data.get("file_name"),
                "timestamp": msg.timestamp.isoformat(),
                "status": msg.status,
                "reactions": await self._serialise_reactions(msg),
            }
        )

        # Send notification to receiver
        sender_profile_data = await self._get_sender_profile_data()
        await self.channel_layer.group_send(
            f"notifications_{receiver.id}",
            {
                "type": "new_message_notification",
                "message": {
                    "title": "New Message",
                    "body": (msg.message or "Sent a file")[:50] + ("..." if len(msg.message or "") > 50 else ""),
                    "sender": self.user.username,
                    "sender_fullname": self.user.get_full_name() or self.user.username,
                    "sender_photo": sender_profile_data.get("photo_url"),
                    "room": self.room_group_name,
                    "message_preview": msg.message[:50] if msg.message else "New file",
                    "timestamp": msg.timestamp.strftime("%H:%M"),
                },
            },
        )

    async def _handle_typing(self, is_typing):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_indicator",
                "username": self.user.username,
                "is_typing": is_typing,
            }
        )

    async def _handle_reaction(self, data):
        msg_id = data.get("message_id")
        emoji = data.get("emoji")
        if not msg_id or not emoji:
            return

        msg = await self._get_message(msg_id)
        if not msg:
            return

        await self._upsert_reaction(msg, self.user, emoji)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_reaction",
                "message_id": msg.id,
                "reactions": await self._serialise_reactions(msg),
            }
        )

    # ------------------------------------------------------------------
    # DB Helpers (unchanged but with safety)
    # ------------------------------------------------------------------
    @database_sync_to_async
    def _get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def _create_message(self, sender, receiver, message, file_path=None, initial_status=0):
        msg = ChatMessage.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            status=initial_status
        )
        if file_path:
            msg.file.name = file_path
            msg.save(update_fields=["file"])
        return msg

    @database_sync_to_async
    def _update_chat_room_last_message(self, message):
        u1, u2 = sorted([message.sender_id, message.receiver_id])
        room, _ = ChatRoom.objects.get_or_create(user1_id=u1, user2_id=u2)
        room.last_message = message
        room.save(update_fields=["last_message"])

    @database_sync_to_async
    def _get_message(self, msg_id):
        try:
            return ChatMessage.objects.get(id=msg_id)
        except ChatMessage.DoesNotExist:
            return None

    @database_sync_to_async
    def _upsert_reaction(self, message, user, emoji):
        MessageReaction.objects.update_or_create(
            message=message, user=user, emoji=emoji
        )

    @database_sync_to_async
    def _serialise_reactions(self, message):
        emojis = list(message.reactions.values_list('emoji', flat=True))
        return dict(Counter(emojis))

    @database_sync_to_async
    def _is_user_online_in_room(self, user):
        return True  # Simplified

    @database_sync_to_async
    def _get_sender_profile_data(self):
        data = {"photo_url": None}
        student = Student.objects.filter(user=self.user).first()
        if student and student.photo:
            data["photo_url"] = student.photo.url
            return data
        teacher = Teacher.objects.filter(user=self.user).first()
        if teacher and teacher.photo:
            data["photo_url"] = teacher.photo.url
        return data

    # In ChatConsumer class (replace the existing _mark_messages_seen)
    async def _mark_messages_seen(self):
        updated_count = await database_sync_to_async(
            ChatMessage.objects.filter(
                receiver=self.user,
                status__lt=2
            ).update(status=2, is_read=True)
        )()

        # In _mark_messages_seen()
        if updated_count > 0:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "status_update",
                    "seen": True
                }
            )

    async def _broadcast_online_status(self, online: bool):
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "status_update", "online": online}
        )

    # Channel Events
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message_id": event["message_id"],
            "message": event["message"],
            "sender_username": event["sender_username"],
            "file_url": event.get("file_url"),
            "file_name": event.get("file_name"),
            "timestamp": event["timestamp"],
            "status": event["status"],
            "reactions": event["reactions"],
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"],
            "is_typing": event["is_typing"],
        }))

    async def message_reaction(self, event):
        await self.send(text_data=json.dumps({
            "type": "reaction",
            "message_id": event["message_id"],
            "reactions": event["reactions"],
        }))

    async def status_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "status",
            "seen": event.get("seen", False),
            "online": event.get("online"),
        }))


# ==============================================
# GLOBAL NOTIFICATION CONSUMER - FIXED
# ==============================================
class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None
        self.user = None

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user or not self.user.is_authenticated:
            logger.warning("Unauthenticated user tried to connect to notifications")
            await self.close()
            return

        self.group_name = f"notifications_{self.user.id}"
        
        # Add to group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        logger.info(f"User {self.user.username} connected to notifications")

        # Send initial data
        try:
            unread = await self._get_unread_count()
            recent = await self._get_recent_messages()
            await self.send(text_data=json.dumps({
                "type": "init_unread",
                "unread_count": unread,
                "recent_messages": recent
            }))
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")

    async def disconnect(self, close_code):
        """SAFE DISCONNECT - No more AttributeError"""
        try:
            if hasattr(self, 'group_name') and self.group_name and hasattr(self, 'channel_name') and self.channel_name:
                await self.channel_layer.group_discard(self.group_name, self.channel_name)
                logger.info(f"User {self.user.username if self.user else 'unknown'} disconnected from notifications")
        except Exception as e:
            logger.error(f"Error in notification disconnect: {e}")

    async def new_message_notification(self, event):
        msg_data = event["message"]
        unread = await self._get_unread_count()
        recent = await self._get_recent_messages()
        
        await self.send(text_data=json.dumps({
            "type": "new_message_notification",
            "message": msg_data,
            "unread_count": unread,
            "recent_messages": recent
        }))

    async def update_unread_count(self, event):
        unread = await self._get_unread_count()
        recent = await self._get_recent_messages()
        
        await self.send(text_data=json.dumps({
            "type": "update_unread_count",
            "unread_count": unread,
            "recent_messages": recent
        }))

    @database_sync_to_async
    def _get_unread_count(self):
        return ChatMessage.objects.filter(
            receiver=self.user,
            is_read=False
        ).count()

    @database_sync_to_async
    def _get_recent_messages(self):
        messages = ChatMessage.objects.filter(
            receiver=self.user
        ).select_related('sender').order_by('-timestamp')[:5]
        
        recent = []
        for msg in messages:
            sender_photo = None
            student = Student.objects.filter(user=msg.sender).first()
            if student and student.photo:
                sender_photo = student.photo.url
            else:
                teacher = Teacher.objects.filter(user=msg.sender).first()
                if teacher and teacher.photo:
                    sender_photo = teacher.photo.url
            
            recent.append({
                "sender_username": msg.sender.username,
                "sender_fullname": msg.sender.get_full_name() or msg.sender.username,
                "sender_photo": sender_photo,
                "message": msg.message[:50] if msg.message else "File",
                "timestamp": msg.timestamp.strftime("%H:%M"),
                "is_read": msg.is_read,
                "url": f"/chat/{msg.sender.username}/"
            })
        return recent