"""
Redis implementation of the StateManager interface.
This implementation uses Redis as the persistent store for task state management.
"""

import json
from typing import List

from redis.asyncio import Redis

from sk_agents.state.state_manager import StateManager
from sk_agents.ska_types import HistoryMultiModalMessage


class RedisStateManager(StateManager):
    """Redis implementation of the StateManager interface.

    This class provides Redis-based persistence for task state management.
    """

    def __init__(self, redis_client: Redis, ttl: int, key_prefix: str = "task_state:"):
        """Initialize the RedisStateManager with a Redis client.

        Args:
            redis_client: An instance of Redis client
            key_prefix: Prefix used for Redis keys (default: "task_state:")
        """
        self._redis = redis_client
        self._key_prefix = key_prefix
        self._ttl = int(ttl) if ttl else None

    def _get_message_key(self, task_id: str) -> str:
        """Generate a Redis key for a task's messages.

        Args:
            task_id: The ID of the task

        Returns:
            A Redis key string for the task's messages
        """
        return f"{self._key_prefix}{task_id}:messages"

    def _get_canceled_key(self, task_id: str) -> str:
        """Generate a Redis key for a task's canceled status.

        Args:
            task_id: The ID of the task

        Returns:
            A Redis key string for the task's canceled status
        """
        return f"{self._key_prefix}{task_id}:canceled"

    async def update_task_messages(
        self, task_id: str, new_message: HistoryMultiModalMessage
    ) -> List[HistoryMultiModalMessage]:
        """Updates the messages for a specific task.

        Appends a new message to the task's message history and returns
        the complete list of messages.

        Args:
            task_id: The ID of the task
            new_message: The new message to add to the task's history

        Returns:
            The complete list of messages for the task
        """
        # Get the Redis key for this task's messages
        message_key = self._get_message_key(task_id)

        # Serialize the new message to JSON with mode='json' to ensure enums are properly serialized
        message_json = json.dumps(new_message.model_dump(mode="json"))

        # Add the new message to the list in Redis
        await self._redis.rpush(message_key, message_json)
        if self._ttl:
            await self._redis.expire(message_key, int(self._ttl))

        # Retrieve all messages for the task
        message_jsons = await self._redis.lrange(message_key, 0, -1)

        # Deserialize each message from JSON
        messages = [
            HistoryMultiModalMessage.model_validate(json.loads(msg))
            for msg in message_jsons
        ]

        return messages

    async def set_canceled(self, task_id: str) -> None:
        """Marks a task as canceled.

        Args:
            task_id: The ID of the task to mark as canceled
        """
        # Set the canceled flag for the task
        await self._redis.set(self._get_canceled_key(task_id), "1", ex=self._ttl)

    async def is_canceled(self, task_id: str) -> bool:
        """Checks if a task is marked as canceled.

        Args:
            task_id: The ID of the task to check

        Returns:
            True if the task is canceled, False otherwise
        """
        # Check if the canceled flag is set
        canceled = await self._redis.get(self._get_canceled_key(task_id))
        return canceled == "1"
