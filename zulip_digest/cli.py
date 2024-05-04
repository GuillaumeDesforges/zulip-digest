from datetime import datetime
import logging
from gpt4all import GPT4All
import click
import json

from gpt4all.gpt4all import sys

from zulip_digest.digest import summarize_messages
from zulip_digest.updates import stream_topic_messages
from zulip_digest.zulip import ZulipClient

TODAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


@click.command()
@click.option(
    "-s",
    "--stream",
    "requested_streams",
    multiple=True,
    help="Streams to process",
    default=[],
)
@click.option(
    "-t",
    "--topic",
    "requested_topics",
    multiple=True,
    help="Topics to process (only 1 stream allowed)",
    default=[],
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output JSON",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
def cli(
    requested_streams: list[str],
    requested_topics: list[str],
    output_json: bool,
    debug: bool,
):
    # setup env
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)

    # check args
    if requested_topics and len(requested_streams) != 1:
        logging.error("Topics can only be specified with a single stream")
        sys.exit(1)

    # setup
    client = ZulipClient(config_file=".zuliprc")
    model = GPT4All("mistral-7b-openorca.gguf2.Q4_0.gguf")

    # run
    streams = client.get_streams()
    missing_streams = set(requested_streams) - set(stream.name for stream in streams)
    if missing_streams:
        logging.error("Unknown streams: %s", missing_streams)
        sys.exit(1)
    found_streams = (
        [stream for stream in streams if stream.name in requested_streams]
        if requested_streams
        else streams
    )

    for stream in found_streams:
        topics = client.get_stream_topics(stream_id=stream.stream_id)
        missing_topics = set(requested_topics) - set(topic.name for topic in topics)
        if missing_topics:
            logging.error("Unknown topics: %s", missing_topics)
            sys.exit(1)
        found_topics = (
            [topic for topic in topics if topic.name in requested_topics]
            if requested_topics
            else topics
        )
        for topic in found_topics:
            messages = list(
                stream_topic_messages(
                    client=client,
                    stream=stream,
                    topic=topic,
                )
            )
            logging.info("Summary for '%s'/'%s'", stream.name, topic.name)
            topic_summary = summarize_messages(
                model=model,
                messages=messages,
                print_progress=True,
            )
            if output_json is True:
                print(
                    json.dumps(
                        {
                            "stream": stream.name,
                            "topic": topic.name,
                            "summary": topic_summary,
                        }
                    )
                )
            else:
                print(topic_summary)
