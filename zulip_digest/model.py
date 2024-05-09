from pydantic import BaseModel

from zulip_digest.api import ZulipMessage, ZulipStream, ZulipTopic


class ZulipTopicExport(BaseModel):
    stream: ZulipStream
    topic: ZulipTopic
    messages: list[ZulipMessage]
