from __future__ import annotations

from dataclasses import dataclass

from aio_pika import IncomingMessage, Message


@dataclass
class EnqueuedMessage:
    payload: str
    message: Message

    @classmethod
    def from_string(cls, message: str) -> EnqueuedMessage:
        m = Message(str.encode(message), message_id=message)
        return cls(message=m, payload=message)


@dataclass
class DequeuedMessage:
    payload: str
    message: IncomingMessage

    @classmethod
    def from_message(cls, message: IncomingMessage) -> DequeuedMessage:
        return cls(message=message, payload=message.body.decode())
