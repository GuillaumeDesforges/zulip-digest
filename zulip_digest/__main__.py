from datetime import datetime
import logging
from gpt4all import GPT4All
import click

from zulip_digest.digest import summarize_messages
from zulip_digest.updates import stream_topic_messages
from zulip_digest.zulip import ZulipClient

TODAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


@click.command()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
def cli(
    debug: bool,
):
    # setup env
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)

    # setup
    client = ZulipClient(config_file=".zuliprc")
    model = GPT4All("mistral-7b-openorca.gguf2.Q4_0.gguf")

    # run
    streams = client.get_streams()
    for stream in streams:
        topics = client.get_stream_topics(stream_id=stream.stream_id)
        for topic in topics:
            messages = list(
                stream_topic_messages(
                    client=client,
                    stream=stream,
                    topic=topic,
                )
            )
            topic_summary = summarize_messages(
                model=model,
                messages=messages,
            )
            logging.info("Summary for %s/%s", stream.name, topic.name)
            print(topic_summary)


cli()
