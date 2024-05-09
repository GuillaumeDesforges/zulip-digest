from typing import Generator

from zulip_digest.api import PZulipClient, ZulipMessage, ZulipStream, ZulipTopic


def export_topic_messages(
    client: PZulipClient,
    stream: ZulipStream,
    topic: ZulipTopic,
) -> Generator[ZulipMessage, None, None]:
    topic_messages = client.get_messages(
        anchor="oldest",
        num_before=0,
        num_after=5000,
        narrow=[
            {"operator": "stream", "operand": stream.name},
            {"operator": "topic", "operand": topic.name},
        ],
        apply_markdown=False,
    )
    for message in topic_messages:
        yield message
