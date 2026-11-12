import redis
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def check_redis_connection():
    try:
        r = redis.Redis.from_url('redis://127.0.0.1:6379')
        r.ping()
        logger.info("Redis connection successful")
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}")
        return False