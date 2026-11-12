from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
from redis.exceptions import ConnectionError as RedisConnectionError

logger = logging.getLogger(__name__)

class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.class_id = self.scope['url_route']['kwargs']['class_id']
        self.group_name = f"attendance_{self.class_id}"
        
        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info(f"WebSocket connected for class {self.class_id}")
        except RedisConnectionError as e:
            logger.error(f"Redis connection error during WebSocket connect: {str(e)}")
            await self.close(code=1011)  # Internal error code
        except Exception as e:
            logger.error(f"Error during WebSocket connect: {str(e)}")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"WebSocket disconnected for class {self.class_id}")
        except RedisConnectionError as e:
            logger.error(f"Redis connection error during WebSocket disconnect: {str(e)}")
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect: {str(e)}")

    async def attendance_update(self, event):
        try:
            await self.send(text_data=json.dumps({
                'status': event['status'],
                'student_name': event.get('student_name', ''),
                'student_id': event.get('student_id', ''),
                'date': event.get('date', ''),
                'message': event.get('message', ''),
                'processing_time': event.get('processing_time', 0)
            }))
            logger.debug(f"Sent attendance update: {event}")
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {str(e)}")

class StaffAttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "attendance_staff"
        
        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.info("WebSocket connected for staff attendance")
        except RedisConnectionError as e:
            logger.error(f"Redis connection error during WebSocket connect for staff: {str(e)}")
            await self.close(code=1011)  # Internal error code
        except Exception as e:
            logger.error(f"Error during WebSocket connect for staff: {str(e)}")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info("WebSocket disconnected for staff attendance")
        except RedisConnectionError as e:
            logger.error(f"Redis connection error during WebSocket disconnect for staff: {str(e)}")
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect for staff: {str(e)}")

    async def attendance_update(self, event):
        try:
            await self.send(text_data=json.dumps({
                'status': event['status'],
                'teacher_name': event.get('teacher_name', ''),
                'teacher_id': event.get('teacher_id', ''),
                'date': event.get('date', ''),
                'message': event.get('message', ''),
                'processing_time': event.get('processing_time', 0)
            }))
            logger.debug(f"Sent staff attendance update: {event}")
        except Exception as e:
            logger.error(f"Error sending WebSocket message for staff: {str(e)}")