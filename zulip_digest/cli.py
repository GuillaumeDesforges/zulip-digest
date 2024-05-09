from datetime import datetime
import logging
import click

from gpt4all.gpt4all import sys

from zulip_digest.export import export_topic_messages
from zulip_digest.api import ZulipClient

TODAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


@click.group()
def _cli():
    pass


@_cli.command()
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
    "-v",
    "--verbose",
    "verbosity",
    help="Enable verbose logging (1: info, 2: debug)",
    count=True,
)
def export(
    requested_streams: list[str],
    requested_topics: list[str],
    verbosity: int,
):
    # setup logging
    log_level = None
    match verbosity:
        case 1:
            log_level = logging.INFO
        case 2:
            log_level = logging.DEBUG
    if log_level:
        logging.basicConfig(level=log_level)

    # check args
    if requested_topics and len(requested_streams) != 1:
        click.echo("Topics can only be specified with a single stream", err=True)
        sys.exit(1)

    # setup
    client = ZulipClient(config_file=".zuliprc")

    # run
    streams = client.get_streams()
    missing_streams = set(requested_streams) - set(stream.name for stream in streams)
    if missing_streams:
        logging.error(
            "Unknown streams %s in %s",
            missing_streams,
            set(stream.name for stream in streams),
        )
        sys.exit(1)
    found_streams = (
        [stream for stream in streams if stream.name in requested_streams]
        if requested_streams
        else streams
    )

    logging.info("Exporting from %s streams", len(found_streams))

    for stream in found_streams:
        logging.info("Exporting from stream %s", stream.name)
        topics = client.get_stream_topics(stream_id=stream.stream_id)
        missing_topics = set(requested_topics) - set(topic.name for topic in topics)
        if missing_topics:
            logging.error(
                "Unknown topics %s in %s",
                missing_topics,
                set(topic.name for topic in topics),
            )
            sys.exit(1)
        found_topics = (
            [topic for topic in topics if topic.name in requested_topics]
            if requested_topics
            else topics
        )
        logging.info("Exporting from %s topics", len(found_topics))
        for topic in found_topics:
            logging.info("Exporting from topic %s", topic.name)
            for message in export_topic_messages(
                client=client,
                stream=stream,
                topic=topic,
            ):
                print(message.model_dump_json())
