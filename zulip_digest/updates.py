import logging
from typing import Generator

from zulip_digest.zulip import PZulipClient, ZulipMessage, ZulipStream, ZulipTopic


def stream_topic_messages(
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
    )
    logging.info(
        "Fetched %s messages for topic '%s' in stream '%s'",
        len(topic_messages),
        topic.name,
        stream.name,
    )
    for message in topic_messages:
        yield message


def stream_stream_messages(
    client: PZulipClient,
    stream: ZulipStream,
) -> Generator[ZulipMessage, None, None]:
    topics = client.get_stream_topics(stream_id=stream.stream_id)
    logging.info(
        "Fetched %s topics in stream '%s'",
        len(topics),
        stream.name,
    )

    for topic in topics:
        yield from stream_topic_messages(
            client=client,
            stream=stream,
            topic=topic,
        )


def stream_all_messages(
    client: PZulipClient,
) -> Generator[ZulipMessage, None, None]:
    streams = client.get_streams()
    logging.info("Fetched %s streams", len(streams))

    for stream in streams:
        yield from stream_stream_messages(
            client=client,
            stream=stream,
        )
