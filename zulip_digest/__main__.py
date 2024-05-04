from datetime import datetime, timedelta
import logging
import zulip
import click

from zulip_digest.updates import fetch_updates
from zulip_digest.zulip import ZulipClient

TODAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


@click.command()
@click.option(
    "--from-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=TODAY,
    help="The date from which to fetch updates",
)
@click.option(
    "--to-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=TODAY + timedelta(days=1),
    help="The date to which to fetch updates",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
def cli(
    from_date: datetime,
    to_date: datetime,
    debug: bool,
):
    # setup env
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)

    # process args
    from_date = from_date.astimezone()
    to_date = to_date.astimezone()
    logging.info("Fetching from %s to %s", from_date, to_date)

    # setup
    client = ZulipClient(config_file=".zuliprc")

    # run
    updates = fetch_updates(
        client=client,
        from_date=from_date,
        to_date=to_date,
    )
    print(updates)


cli()
