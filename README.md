# zulip digest

Extract and summarize conversations on Zulip with "the power of AI"_TM_.

## Usage

### Export messages

Export messages from a topic in a stream to stdout in JSONL.

```bash
zulip-digest export -s STREAM_NAME -t TOPIC_NAME
```

Export messages from all topics in a stream to stdout in JSONL.

```bash
zulip-digest export -s STREAM_NAME
```

Export messages from all topics in every stream to stdout in JSONL.

```bash
zulip-digest export
```

Reference:

```console
$ zulip-digest export --help
Usage: zulip-digest export [OPTIONS]

Options:
  -s, --stream TEXT  Streams to process
  -t, --topic TEXT   Topics to process (only 1 stream allowed)
  -v, --verbose      Enable verbose logging (1: info, 2: debug)
  --help             Show this message and exit.
```

### Summarize

Summarize messages from a topic in a stream from stdin (same JSONL as in the export).

__TODO__

## Install

Requirements: Python 3+

Install from the repository:

```bash
pip install https+git://github.com/GuillaumeDesforges/zulip-digest.git
```

Then create a file `.zuliprc` as specified in the [Zulip documentation](https://zulip.com/api/configuring-python-bindings#configuration-keys-and-environment-variables).

```
[api]
key=<API key from the web interface>
email=<your email address>
site=<your Zulip server's URI>
...
```
