from datetime import datetime
from dataclasses import dataclass
import logging

from zulip_digest.zulip import PZulipClient, ZulipMessage, ZulipTopic


@dataclass(frozen=True)
class Updates:
    messages: list[ZulipMessage]


def fetch_updates(
    client: PZulipClient,
    from_date: datetime,
    to_date: datetime,
) -> Updates:
    streams = {stream.stream_id: stream for stream in client.get_streams()}
    logging.info("Fetched %s streams", len(streams))

    # stream_topics: dict[int, list[ZulipTopic]] = {}
    # for stream in streams.values():
    #     stream_topics[stream.stream_id] = client.get_stream_topics(
    #         stream_id=stream.stream_id
    #     )
    #     logging.info(
    #         "Fetched %s topics in stream '%s'",
    #         len(stream_topics),
    #         stream.name,
    #     )

    messages: list[ZulipMessage] = []
    for stream in streams.values():
        stream_messages = client.get_messages(
            anchor="oldest",
            narrow=[{"operator": "stream", "operand": stream.name}],
        )
        logging.info(
            "Fetched %s messages for stream '%s'",
            len(stream_messages),
            stream.name,
        )
        messages.extend(stream_messages)
    # for topics_stream_id, topics in stream_topics.items():
    #     for topic in topics:
    #         topic_messages = client.get_messages(
    #             anchor="newest",
    #             narrow=[{"operator": "topic", "operand": topic.name}],
    #         )
    #         logging.info(
    #             "Fetched %s messages for topic '%s' in stream '%s'",
    #             len(topic_messages),
    #             topic.name,
    #             streams[topics_stream_id].name,
    #         )
    #         messages.extend(topic_messages)

    return Updates(messages=messages)
