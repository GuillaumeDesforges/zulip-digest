from datetime import datetime
from dataclasses import dataclass
import logging
from typing import Generator

from zulip_digest.zulip import PZulipClient, ZulipMessage, ZulipStream, ZulipTopic


def fetch_topic(
    client: PZulipClient,
    from_date: datetime,
    to_date: datetime,
    stream: ZulipStream,
    topic: ZulipTopic,
) -> Generator[ZulipMessage, None, None]:
    topic_messages = client.get_messages(
        anchor="oldest",
        num_before=1,
        num_after=1000,
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


def fetch_stream(
    client: PZulipClient,
    from_date: datetime,
    to_date: datetime,
    stream: ZulipStream,
) -> Generator[ZulipMessage, None, None]:
    topics = client.get_stream_topics(stream_id=stream.stream_id)
    logging.info(
        "Fetched %s topics in stream '%s'",
        len(topics),
        stream.name,
    )

    for topic in topics:
        yield from fetch_topic(
            client=client,
            from_date=from_date,
            to_date=to_date,
            stream=stream,
            topic=topic,
        )


def fetch_all_streams(
    client: PZulipClient,
    from_date: datetime,
    to_date: datetime,
) -> Generator[ZulipMessage, None, None]:
    streams = client.get_streams()
    logging.info("Fetched %s streams", len(streams))

    for stream in streams:
        yield from fetch_stream(
            client=client,
            from_date=from_date,
            to_date=to_date,
            stream=stream,
        )
