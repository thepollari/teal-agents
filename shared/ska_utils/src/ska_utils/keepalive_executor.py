import asyncio
import logging
from collections.abc import AsyncGenerator, Awaitable
from typing import TypeVar

from pydantic import BaseModel


class KeepaliveMessage(BaseModel):
    message: str = "keepalive"


TResponseType = TypeVar("TResponseType")  # Return type of the main task


async def execute_with_keepalive(
    task_coro: Awaitable[TResponseType],
    keepalive_interval_seconds: float = 30.0,
    keepalive_poll_interval_seconds: float = 1.0,
    logger: logging.Logger | None = None,
) -> AsyncGenerator[KeepaliveMessage | TResponseType, None]:
    """
    Executes a long-running coroutine while periodically yielding keepalive messages.

    Args:
        task_coro: The coroutine to execute
        keepalive_interval_seconds: Seconds between keepalive messages
        keepalive_poll_interval_seconds: How frequently to check the queue
        logger: Optional logger for error reporting

    Yields:
        Keepalive messages while the task is running and the final task result when complete
    """
    keepalive_queue: asyncio.Queue[KeepaliveMessage] = asyncio.Queue()

    async def run_keepalive() -> None:
        try:
            while True:
                await asyncio.sleep(keepalive_interval_seconds)
                keepalive_queue.put_nowait(KeepaliveMessage())
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if logger:
                logger.error(f"Keepalive exception: {e}")

    keepalive_task: asyncio.Task[None] | None = asyncio.create_task(run_keepalive())
    try:
        main_task: asyncio.Task[TResponseType] = asyncio.create_task(task_coro)
        while not main_task.done():
            try:
                message: KeepaliveMessage = await asyncio.wait_for(
                    keepalive_queue.get(), keepalive_poll_interval_seconds
                )
                yield message
            except TimeoutError:
                pass

        # Get and yield the final result
        result: TResponseType = await main_task
        yield result
    except Exception as e:
        if logger:
            logger.error(f"Task exception: {e}")
        raise
    finally:
        # Always ensure keepalive task is cancelled
        if keepalive_task and not keepalive_task.done():
            keepalive_task.cancel()
            try:
                await asyncio.wait_for(keepalive_task, 1.0)
            except (asyncio.CancelledError, TimeoutError):
                pass
