import redis.asyncio as redis
import json
from typing import Dict, Any, Optional
import os

class SessionManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a session from Redis.
        """
        session_data = await self.redis_client.get(f"session:{session_id}")
        if session_data:
            return json.loads(session_data)
        return None

    async def save_session(self, session_id: str, session_data: Dict[str, Any], ttl: int = 3600):
        """
        Saves a session to Redis with a TTL.
        """
        await self.redis_client.set(f"session:{session_id}", json.dumps(session_data), ex=ttl)

# In a real application, these would be configured from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

def get_session_manager() -> SessionManager:
    """
    Initializes and returns the SessionManager.
    """
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    return SessionManager(redis_client)

# Example of how to use it:
# session_manager = get_session_manager()
# await session_manager.save_session("my-session-id", {"history": ["hello"]})
# session = await session_manager.get_session("my-session-id")
