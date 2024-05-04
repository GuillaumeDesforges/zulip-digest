from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Literal, Protocol, Type, TypedDict

from pydantic import BaseModel
import zulip


class ZulipStream(BaseModel):
    stream_id: int
    name: str
    description: str
    date_created: datetime


class ZulipTopic(BaseModel):
    max_id: int
    name: str


class ZulipMessage(BaseModel):
    id: int
    content: str
    sender_id: int
    sender_full_name: str
    stream_id: int
    subject: str
    timestamp: datetime


class ZulipNarrow(TypedDict):
    operator: Literal["sender", "stream", "topic"]
    operand: str


class PZulipClient(Protocol):
    def get_streams(self) -> list[ZulipStream]: ...
    def get_stream_topics(self, stream_id: int) -> list[ZulipTopic]: ...
    def get_messages(
        self,
        anchor: Literal["newest", "oldest", "first_unread"] | int | None = None,
        num_before: int = 1000,
        num_after: int = 1000,
        narrow: list[ZulipNarrow] | None = None,
    ) -> list[ZulipMessage]: ...


class ZulipGetStreamsResponse(BaseModel):
    streams: list[ZulipStream]


class ZulipGetStreamTopicsResponse(BaseModel):
    topics: list[ZulipTopic]


class ZulipGetMessagesResponse(BaseModel):
    messages: list[ZulipMessage]
    found_anchor: bool
    found_newest: bool
    found_oldest: bool


def _validate_response(response: dict):
    if response["result"] == "success":
        return response["msg"]
    raise ValueError(response["msg"])


class ZulipClient(PZulipClient):
    def __init__(self, config_file: str) -> None:
        self._client = zulip.Client(config_file=config_file)

    def get_streams(self) -> list[ZulipStream]:
        response = self._client.get_streams()
        logging.debug(response)
        _validate_response(response)
        parsed_response = ZulipGetStreamsResponse.model_validate(response)
        return parsed_response.streams

    def get_stream_topics(self, stream_id: int) -> list[ZulipTopic]:
        response = self._client.get_stream_topics(stream_id)
        logging.debug(response)
        _validate_response(response)
        parsed_response = ZulipGetStreamTopicsResponse.model_validate(response)
        return parsed_response.topics

    def get_messages(
        self,
        anchor: Literal["newest", "oldest", "first_unread"] | int | None,
        num_before: int = 1000,
        num_after: int = 1000,
        narrow: list[ZulipNarrow] | None = None,
    ) -> list[ZulipMessage]:
        response = self._client.get_messages(
            dict(
                anchor=anchor,
                num_before=num_before,
                num_after=num_after,
                narrow=narrow,
                include_anchor=True,
            )
        )
        logging.debug(response)
        _validate_response(response)
        parsed_response = ZulipGetMessagesResponse.model_validate(response)
        if type(anchor) is int and not parsed_response.found_anchor:
            raise ValueError(f"Anchor {anchor} not found")
        if anchor == "newest" and not parsed_response.found_newest:
            raise ValueError("Newest message not found")
        if anchor == "oldest" and not parsed_response.found_oldest:
            raise ValueError("Oldest message not found")
        return parsed_response.messages
