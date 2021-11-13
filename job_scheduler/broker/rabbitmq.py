from __future__ import annotations

import asyncio
import typing as t

import aio_pika
import structlog
from aio_pika.channel import Channel
from aio_pika.pool import Pool

from job_scheduler.config import config

from .base import ScheduleBroker
from .messages import DequeuedMessage, EnqueuedMessage

logger = structlog.get_logger(__name__)


async def _get_connection() -> aio_pika.Connection:
    sleep_time = 3
    while True:
        try:
            parts = config.broker.url.split("://")
            safe_string = f"{parts[0]}://{config.broker.username}:***{config.broker.password[-5:]}@{parts[1]}"
            conn_string = f"{parts[0]}://{config.broker.username}:{config.broker.password}@{parts[1]}"
            logger.info(f"Instantiating rabbitmq broker at {safe_string}")
            conn: aio_pika.Connection = await aio_pika.connect_robust(conn_string)
        except (ConnectionError, aio_pika.exceptions.IncompatibleProtocolError):
            logger.warning(
                f"Unable to instantiate rabbitmq broker at {config.broker.url}. "
                f"Retrying in {sleep_time} seconds.",
                exc_info=True,
            )
            asyncio.sleep(sleep_time)
        else:
            logger.info(f"Broker sucessfully instantiated.")
            return conn


_connection_pool: Pool = Pool(_get_connection, max_size=2)


async def _get_channel() -> aio_pika.Channel:
    async with _connection_pool.acquire() as connection:
        return await connection.channel()


_channel_pool: Pool = Pool(_get_channel, max_size=10)


class RabbitMQBroker(ScheduleBroker):
    def __init__(self, channel: aio_pika.Channel, queue: aio_pika.Queue):
        self.queue: aio_pika.Queue = queue
        self.channel: Channel = channel

    @classmethod
    async def get_broker(cls) -> RabbitMQBroker:
        async with _channel_pool.acquire() as channel:
            await channel.set_qos(prefetch_count=config.broker.prefetch_count)
            queue = await channel.declare_queue(config.broker.queue_name, durable=True)
            return cls(channel, queue)

    async def publish(self, *messages: str) -> t.Sequence[EnqueuedMessage]:
        assert self.channel.default_exchange is not None

        published = []
        for m in messages:
            enqueued_message = EnqueuedMessage.from_string(m)
            await self.channel.default_exchange.publish(
                enqueued_message.message,
                self.queue.name,
            )
            published.append(enqueued_message)
        return published

    async def get(self) -> DequeuedMessage:
        """
        Retrieve a message from the Queue, or block until one is available
        """
        while True:
            try:
                message = await self.queue.get(timeout=1, fail=True)
            except aio_pika.exceptions.QueueEmpty:
                await asyncio.sleep(1)
            else:
                break

        assert message is not None
        return DequeuedMessage.from_message(message)

    async def drain(self, limit: int = 100) -> t.Sequence[DequeuedMessage]:
        messages = [await self.get()]

        while True:
            try:
                message = await self.queue.get(timeout=1, fail=True)
            except aio_pika.exceptions.QueueEmpty:
                return messages
            else:
                assert message is not None
                dm = DequeuedMessage.from_message(message)
                messages.append(dm)
                if len(messages) == limit:
                    return messages

    async def ack(self, *messages: DequeuedMessage):
        for m in messages:
            m.message.ack()

    async def shutdown(self):
        await self.channel.close()
